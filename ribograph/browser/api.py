import re
from functools import lru_cache, reduce
import pandas as pd
from scipy.stats import spearmanr
from cachetools.keys import hashkey
from cachetools import TTLCache, cached

from django.shortcuts import render, get_object_or_404, redirect
from django.http import (
    HttpResponse,
    Http404,
    HttpResponseBadRequest,
    JsonResponse,
    HttpResponseNotFound,
)
from django.views.decorators.gzip import gzip_page

from .models import Experiment, Project, Reference
from .Fasta import FastaFile

import ribopy
from ribopy import Ribo
from ribopy.core.get_gadgets import get_region_boundaries, get_reference_names
import time

def camelCase(st: str):
    """
    Convert a given string to camelCase
    """
    output = "".join(x for x in st.title() if x.isalnum())
    return output[0].lower() + output[1:]

@cached(cache=TTLCache(maxsize=64, ttl=300))
def get_ribo(experiment: Experiment) -> Ribo:
    """
    Create a ribo object for the given experiment with the appropriate aliasing.
    """
    alias = None
    if experiment.transcript_regex:
        alias = lambda x: re.search(experiment.transcript_regex, x).group(1)
    return Ribo(experiment.ribo_file_path, alias=alias)


def request_key(*args, **kwargs):
    """
    Hashes an API request by its path. This is how we tell if a request is cached.
    """
    request = args[0]
    return hashkey(request.get_full_path())


def make_experiment_api_registrar():
    """
    Returns a decorator that wraps experiment level APIs. This decorater
    centralizes some common logic, including getting the ribo and experiment 
    objects, authenticating requests, and caching responses.
    """
    registry = {}

    def registrar(func):
        def api_decorator(f):
            @cached(cache=TTLCache(maxsize=128, ttl=600), key=request_key)
            @gzip_page
            def wrapper(*args, **kwargs):
                request = args[0]
                assert "experiment_id" in kwargs and "project_id" not in kwargs
                experiment = Experiment.objects.get(id=kwargs["experiment_id"])
                # check permissions - either the project is public or a user is logged in
                if not (request.user or experiment.project.public):
                    raise Http404
                ribo = get_ribo(experiment)
                result = f(ribo, experiment, *args, **kwargs)
                if not isinstance(result, HttpResponse):
                    # inject this info into every response
                    result["experiment"] = experiment.name
                    result["min"] = int(ribo.minimum_length)
                    result["totalReads"] = int(
                        ribo._handle["experiments"][experiment.name].attrs[
                            "total_reads"
                        ]
                    )
                if not isinstance(result, HttpResponse):
                    result = JsonResponse(result)
                return result

            return wrapper

        registry[camelCase(func.__name__)] = api_decorator(func)
        return api_decorator(func)

    registrar.all = registry
    return registrar


def make_project_api_registrar():
    """
    Returns a decorator that wraps experiment level APIs. This decorater
    centralizes some common logic, including getting the project
    object, authenticating requests, and caching responses.
    """
    registry = {}

    def registrar(func):
        def api_decorator(f):
            @cached(cache=TTLCache(maxsize=128, ttl=600), key=request_key)
            @gzip_page
            def wrapper(*args, **kwargs):
                request = args[0]
                assert "project_id" in kwargs and "experiment_id" not in kwargs
                project = Project.objects.get(id=kwargs["project_id"])
                if not request.user or project.public:
                    raise Http404
                result = f(project, *args, **kwargs)
                if not isinstance(result, HttpResponse):
                    result = JsonResponse(result)
                return result

            return wrapper

        registry[func.__name__] = api_decorator(func)
        return api_decorator(func)

    registrar.all = registry
    return registrar


register_experiment_api = make_experiment_api_registrar()
register_project_api = make_experiment_api_registrar()


@register_experiment_api
def get_metadata(ribo, experiment: Experiment, *args, **kwargs):
    return {
        "min": int(ribo.minimum_length),
        "max": int(ribo.maximum_length),
        "ribopyVersion": ribo.ribopy_version,
    }


@register_experiment_api
def get_region_percentages(ribo, experiment: Experiment, *args, **kwarg):
    """
    Returns a triplet of percentages for the regions (5' UTR, CDS, 3' UTR) for each read length.
    """
    region_counts = [
        ribo.get_region_counts(
            experiments=[experiment.name],
            region_name=region,
            range_lower=ribo.minimum_length,
            range_upper=ribo.maximum_length,
            sum_lengths=False,
        ).rename(columns={experiment.name: region})
        for region in ("UTR5", "CDS", "UTR3")
    ]
    combined_region_counts = reduce(lambda x, y: x.join(y), region_counts)
    return combined_region_counts.to_dict(orient="split")


@register_experiment_api
def get_length_distribution(ribo, experiment: Experiment, *args, **kwargs):
    """
    Get the distribution of read lengths for this experiment.
    """
    length_df = ribo.get_length_dist(region_name="CDS", experiments=[experiment.name])
    length_dist = list(length_df[experiment.name])
    return {"min": int(length_df.index.values[0]), "data": length_dist}


@register_experiment_api
def get_metagene_counts(ribo, experiment: Experiment, request, *args, **kwargs):
    """
    Get the metagene counts around the start or stop site for this experiment.
    User must provide the site as a URL paramater (either 'start' or 'stop')
    """
    site_type = request.GET.get("site")
    if site_type is None:
        return HttpResponseBadRequest(
            "site type must be provided as a url parameter (either 'start' or 'stop')"
        )
    df = ribo.get_metagene(
        site_type=site_type,
        experiments=[experiment.name],
        range_lower=ribo.minimum_length,
        range_upper=ribo.maximum_length,
        sum_lengths=False,
    )
    df = df.reset_index()
    return (
        df[df["experiment"] == experiment.name]
        .set_index(keys=["read_length"])
        .drop(columns=["experiment"])
        .to_dict(orient="split")
    )


@register_experiment_api
def list_genes(ribo, experiment: Experiment, *args, **kwargs):
    """
    Return a dict of the genes in an experiment mapped to and sorted by their frequency in the CDS.
    """
    df = ribo.get_region_counts("CDS", sum_references=False, alias=(ribo.alias != None))
    df = df.sort_values(by=[experiment.name], ascending=False)
    genes = df.to_dict()[experiment.name]
    return {"genes": genes}


@cached(cache=TTLCache(maxsize=128, ttl=3600))
def get_sequence_dict(reference: Reference, ribo: Ribo, alias):
    """
    For a given reference and alias, return a dict of aliased gene name to sequence mappings.
    """
    if reference is None:
        return None

    transcript_names = ribo.transcript_names
    reference_file_path = reference.reference_file_path
    fasta = FastaFile(reference_file_path)
    fasta_dict = {e.header: e.sequence for e in fasta}
    sequence_dict = {
        alias(transcript): fasta_dict[transcript] for transcript in transcript_names
    }
    return sequence_dict


@cached(cache=TTLCache(maxsize=128, ttl=3600))
def get_cds_range_lookup(ribo: Ribo):
    """
    Create a dict of gene to region ranges, so that the CDS range can be found for a given experiment.
    """
    names = get_reference_names(ribo._handle)
    if ribo.alias != None:
        names = map(ribo.alias.get_alias, names)
    boundaries = get_region_boundaries(ribo._handle)
    boundary_lookup = dict(zip(list(names), boundaries))
    return boundary_lookup


@register_experiment_api
def get_coverage(ribo, experiment: Experiment, request, *args, **kwargs):
    """
    Get the coverage for a particular gene in an experiment. Also returns the CDS range
    for the gene and the sequence.
    """
    gene = request.GET.get("gene")
    if gene is None:
        return HttpResponseBadRequest(
            "gene name must be provided as a url parameter"
        )
    cds_range = get_cds_range_lookup(ribo)[gene][1]
    df = ribo.get_transcript_coverage(
        experiment.name, alias=(ribo.alias != None), transcript=gene
    )
    sequence_dict = get_sequence_dict(
        experiment.reference,
        ribo=ribo,
        alias=(ribo.alias.get_alias if ribo.alias != None else lambda x: x),
    )
    return {
        "cdsRange": (int(cds_range[0]), int(cds_range[1]) - 1),
        "coverage": df.to_dict(orient="split"),
        "gene": gene,
        "geneSequence": sequence_dict[gene] if sequence_dict else None,
    }


@register_experiment_api
def list_experiments(ribo, experiment: Experiment, request, *args, **kwargs):
    """
    List all experiments compatible with the given experiment for the purposes of comparing coverage plots
    """
    experiments = Experiment.objects.filter(
        reference_digest=experiment.reference_digest
    )
    return {
        "experiments": [
            {"id": x.id, "name": x.name, "project": x.project.name} for x in experiments
        ]
    }


@register_project_api
def get_gene_correlations(project: Project, *args, **kwargs):
    ...
