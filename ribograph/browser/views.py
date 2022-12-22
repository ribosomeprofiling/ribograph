from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib.auth.models import User, Group

from browser.models import Project, Experiment, Reference
from browser.forms import (
    ProjectForm,
    NewUserForm,
    UploadRiboFileForm,
    ExperimentPickFormSet,
    ExperimentDescriptionForm,
    ProjectDescriptionForm,
    ReferenceForm,
    ReferenceUploadForm,
    ReferenceEditForm,
    ExperimentReferenceForm,
)
from django.contrib.auth import authenticate

from .tables import ProjectTable, ExperimentTable, ReferenceTable

from django.contrib import messages

from django_tables2 import RequestConfig

from ribopy import Ribo

import os

from hashlib import md5

from ribograph.settings import RIBO_FOLDER, REFERENCE_FOLDER

import shutil

from .Fasta import FastaFile

import re

#############################################################################


def setup_admin_user(request):
    return render(request, "browser/setup_admin_user.html", {})


def index(request):

    # If there are no users, then the system is run for the first time.
    # So let them create an admin account.
    if len(User.objects.all()) == 0:
        return HttpResponseRedirect(reverse("browser:add_admin_user"))

    return render(request, "browser/index.html")


#############################################################################


@login_required
def coverage(request, experiment_id):
    this_experiment = Experiment.objects.get(id=experiment_id)
    this_project = this_experiment.project

    reference_form = ExperimentReferenceForm(instance=this_experiment)

    if request.method == "POST":
        reference_form = ExperimentReferenceForm(request.POST, instance=this_experiment)
        if reference_form.is_valid():
            reference_form.save()
            return HttpResponseRedirect(
                reverse("browser:coverage", args=[experiment_id])
            )

    context = {
        "project": this_project,
        "experiment": this_experiment,
        "reference_form": reference_form,
    }
    return render(request, "browser/coverage.html", context)


@login_required
def offset(request, experiment_id):
    this_experiment = Experiment.objects.get(id=experiment_id)
    this_project = this_experiment.project

    context = {
        "project": this_project,
        "experiment": this_experiment,
    }
    return render(request, "browser/offset.html", context)


@login_required
def add_project(request):
    context = {}

    if request.method == "POST":
        context["form"] = ProjectForm(request.POST)
        if context["form"].is_valid():
            this_project = context["form"].save(commit=False)
            this_project.owner = request.user
            this_project.save()
            return HttpResponseRedirect(
                reverse("browser:project_details", args=[this_project.id])
            )

    else:
        context["form"] = ProjectForm()

    return render(request, "browser/add_project.html", context)


@login_required
def project_details(request, project_id):
    context = {}
    return render(request, "browser/project_details.html", context)


def add_admin_user(request):

    # If there are already registered users, then redirect to the index page.
    if len(User.objects.all()) > 0:
        return HttpResponseRedirect(reverse("browser:index"))

    context = {}

    if request.method == "POST":
        context["form"] = NewUserForm(request.POST)
        if context["form"].is_valid():
            this_user = context["form"].save()
            authenticate(
                username=context["form"].cleaned_data.get("username"),
                password=context["form"].cleaned_data.get("password"),
            )

            return HttpResponseRedirect(reverse("browser:index"))

    else:
        context["form"] = NewUserForm()

    return render(request, "browser/add_admin_user.html", context)


@login_required
def project_details(request, project_id):
    this_project = Project.objects.get(id=project_id)
    experiments = Experiment.objects.filter(project=this_project)
    experiment_table = ExperimentTable(experiments)

    experiments_exist = len(experiments) > 0

    upload_form = UploadRiboFileForm(initial={"project_id": project_id})

    context = {
        "project": this_project,
        "experiments_exist": experiments_exist,
        "experiment_table": experiment_table,
        "upload_form": upload_form,
    }

    if request.method == "POST":
        form = UploadRiboFileForm(request.POST, request.FILES)
        if form.is_valid():
            os.makedirs(os.path.join("/tmp", "ribo"), exist_ok=True)

            file_digest = handle_uploaded_file(request.FILES["ribo_file"])

            project_id = form.cleaned_data["project_id"]
            project = Project.objects.get(id=project_id)
            return HttpResponseRedirect(
                reverse("browser:confirm_ribo_file", args=[project_id, file_digest])
            )

        context["upload_form"] = form
        return render(request, "browser/project_details.html", context)

    return render(request, "browser/project_details.html", context)


def digest_reference(ribo_handle):
    """
    We take the transcript names and concatanate transcript lengths to them.
    Then we hash the resulting value.
    If the hashed values are same for two experiments, we can
    assume that they come from the same reference.
    """
    transcript_names = ribo_handle.transcript_names
    transcript_lengths_dict = ribo_handle.transcript_lengths
    transcript_lengths = [
        str(transcript_lengths_dict[t_name]) for t_name in transcript_names
    ]

    transcript_names_string = ",".join(transcript_names)
    transcript_lengths_string = ",".join(transcript_lengths)

    string_to_be_digested = transcript_names_string + transcript_lengths_string
    transcript_hash = md5()
    transcript_hash.update(string_to_be_digested.encode("ascii"))

    return transcript_hash.hexdigest()


##########################################################################################


def determine_transcript_regex(ribo_path):
    """
    If the transcript name has many "|"s, then
    our guess is it is coming from Appris.
    So we will pick the names between 3rd and fourth "|"s.
    If not, then we will return empty string.
    """
    this_handle = Ribo(ribo_path)
    transcript_names = this_handle.transcript_names

    number_of_bars = len(re.findall(r"\|", transcript_names[0]))

    # If there are many bars, we assume that it is coming from the appris reference
    # So we pich the 5th element which is
    # GeneName-TranscriptNumber
    # E.g.: Rfpl4-201
    regex = ""

    if number_of_bars > 8:
        regex = "^(?:[^|]*\|){4}([^|]*)\|.*$"

    # Mak sure the alias coming from the regular expression is accepted by ribo
    if regex:
        try:
            this_ribo = Ribo(ribo_path, alias=lambda x: re.search(regex, x).group(1))
        except:
            return ""

    return regex


def confirm_ribo_file(request, project_id, file_digest):

    file_path = os.path.join("/tmp/ribo", file_digest + ".ribo")
    this_project = Project.objects.get(id=project_id)

    if request.method == "POST":
        experiment_form_set = ExperimentPickFormSet(request.POST)
        if experiment_form_set.is_valid():
            os.makedirs(os.path.join(RIBO_FOLDER, this_project.name), exist_ok=True)
            source_path = file_path
            target_path = os.path.join(
                RIBO_FOLDER, this_project.name, file_digest + ".ribo"
            )
            shutil.move(source_path, target_path)

            this_ribo = Ribo(target_path)
            this_ribo_reference_digest = digest_reference(this_ribo)
            transcript_regex = determine_transcript_regex(target_path)

            ### Make sure that another experiment with the same name does not exist

            duplicate_experiment_names = []
            existing_experiment_names = map(
                lambda x: x.name, Experiment.objects.filter(project=this_project)
            )

            for form in experiment_form_set:
                experiment_name = form.cleaned_data.get("experiment")
                selected = form.cleaned_data.get("selected")
                if selected:
                    if experiment_name in existing_experiment_names:
                        duplicate_experiment_names.append(experiment_name)

            if duplicate_experiment_names:
                error_message = (
                    "The following experiments already exist in this project: "
                    + ", ".join(duplicate_experiment_names)
                )
                return erase_reference(request, error_message)

            for form in experiment_form_set:
                experiment_name = form.cleaned_data.get("experiment")
                selected = form.cleaned_data.get("selected")
                if selected:
                    this_experiment = Experiment(
                        name=experiment_name,
                        project=this_project,
                        ribo_file_path=target_path,
                        reference_digest=this_ribo_reference_digest,
                        transcript_regex=transcript_regex,
                    )
                    this_experiment.save()

        return HttpResponseRedirect(
            reverse("browser:project_details", args=[project_id])
        )
    else:
        myribo = Ribo(file_path)

        experiments = myribo.experiments
        form_initial = [{"experiment": e, "selected": True} for e in experiments]

        experiment_form_set = ExperimentPickFormSet(initial=form_initial)
        for i, experiment in enumerate(experiments):
            experiment_form_set[i].fields["selected"].label = experiment

        return render(
            request,
            "browser/confirm_ribo_file.html",
            {"experiments": experiments, "form_set": experiment_form_set},
        )


def handle_uploaded_file(file):
    my_hash_raw = md5()
    chunk = file.read(8192)
    while chunk:
        my_hash_raw.update(chunk)
        chunk = file.read(8192)

    file_name = "{}.ribo".format(my_hash_raw.hexdigest())
    tmp_ribo_path = os.path.join("/tmp", "ribo", file_name)

    file.seek(0)
    with open(tmp_ribo_path, "wb") as output_stream:
        output_stream.write(file.read())

    return my_hash_raw.hexdigest()


def validate_ribo_file(ribo_file):
    return True


##########################################################################


@login_required
def experiment_details(request, experiment_id):
    this_experiment = Experiment.objects.get(id=experiment_id)
    this_project = this_experiment.project

    if request.method == "POST":
        description_form = ExperimentDescriptionForm(
            request.POST, instance=this_experiment
        )

        if description_form.is_valid():
            description_form.save()
            this_experiment = Experiment.objects.get(id=experiment_id)

    description_form = ExperimentDescriptionForm(instance=this_experiment)

    context = {
        "project": this_project,
        "experiment": this_experiment,
        "description_form": description_form,
    }

    return render(request, "browser/experiment_details.html", context)


##########################################################################


def download_ribo(request, experiment_id):
    this_experiment = Experiment.objects.get(id=experiment_id)
    this_project = this_experiment.project
    file_path = this_experiment.ribo_file_path

    if os.path.exists(file_path):
        with open(file_path, "rb") as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response["Content-Disposition"] = (
                "inline; filename=" + this_experiment.name + ".ribo"
            )
        return response

    raise Http404


##########################################################################


def delete_experiment(request, experiment_id):
    context = dict()

    this_experiment = Experiment.objects.get(id=experiment_id)
    context["experiment"] = this_experiment
    context["project"] = this_experiment.project

    return render(request, "browser/delete_experiment.html", context)


##########################################################################


def _erase_experiment(this_experiment):
    experiment_ribo_file = this_experiment.ribo_file_path

    this_experiment.delete()

    other_experiments_with_same_ribo_file = Experiment.objects.filter(
        ribo_file_path=experiment_ribo_file
    )

    if len(other_experiments_with_same_ribo_file) == 0:
        os.remove(experiment_ribo_file)


def erase_experiment(request, experiment_id):
    # TODO: MAke sure that the user has the right to delete

    context = dict()

    this_experiment = Experiment.objects.get(id=experiment_id)
    this_project = this_experiment.project

    _erase_experiment(this_experiment)

    return HttpResponseRedirect(
        reverse("browser:project_details", args=[this_project.id])
    )


##########################################################################


def delete_project(request, project_id):
    context = dict()

    context["project"] = Project.objects.get(id=project_id)

    return render(request, "browser/delete_project.html", context)


##########################################################################


def erase_project(request, project_id):
    this_project = Project.objects.get(id=project_id)

    experiments_of_project = Experiment.objects.filter(project=this_project)

    for e in experiments_of_project:
        _erase_experiment(e)

    this_project.delete()

    return HttpResponseRedirect(reverse("browser:index"))


##########################################################################


def edit_project_description(request, project_id):

    this_project = Project.objects.get(id=project_id)
    context = dict()

    context["project"] = this_project
    form = ProjectDescriptionForm(instance=this_project)

    if request.method == "POST":

        form = ProjectDescriptionForm(request.POST, instance=this_project)

        if form.is_valid():
            form.save()

            return HttpResponseRedirect(
                reverse("browser:project_details", args=[project_id])
            )
        else:
            return render(request, "browser/edit_project_description.html", context)

    context["form"] = form

    return render(request, "browser/edit_project_description.html", context)


##########################################################################


@login_required
def references(request):

    references = Reference.objects.all()

    reference_table = ReferenceTable(references)

    context = {
        "reference_table": reference_table,
        "references_exist": len(references) > 0,
    }

    return render(request, "browser/list_references.html", context)


##########################################################################


@login_required
def add_reference(request):
    form = ReferenceUploadForm()

    context = {
        "form": form,
    }

    if request.method == "POST":
        form = ReferenceUploadForm(request.POST, request.FILES)
        if form.is_valid():
            os.makedirs(os.path.join("/tmp", "reference"), exist_ok=True)
            file_digest = handle_reference_file(request.FILES["reference_file"])

            return HttpResponseRedirect(
                reverse("browser:record_reference", args=[file_digest])
            )
        else:
            print(form.errors)

        # Change the next line when you are finished with this
        return render(request, "browser/list_references.html", context)

    return render(request, "browser/add_reference.html", context)


##########################################################################

##########################################################################


@login_required
def record_reference(request, reference_hash):
    file_path = "/tmp/reference/{}.fa.gz".format(reference_hash)

    if request.method == "POST":
        form = ReferenceForm(request.POST)

        if form.is_valid():

            source_path = os.path.join("/tmp/reference/{}.gz".format(reference_hash))
            target_path = os.path.join(REFERENCE_FOLDER, reference_hash + ".gz")
            shutil.move(source_path, target_path)

            this_reference = Reference(
                name=form.cleaned_data.get("name"),
                organism=form.cleaned_data.get("organism"),
                owner=request.user,
                reference_file_path=os.path.join(
                    REFERENCE_FOLDER, reference_hash + ".gz"
                ),
            )
            this_reference.save()
            return HttpResponseRedirect(reverse("browser:references"))

        return render(request, "browser/list_references.html", {})
    else:
        form = ReferenceForm(initial={"file_hash": reference_hash})

        return render(
            request,
            "browser/record_reference.html",
            {"form": form},
        )


##########################################################################


def handle_reference_file(file):
    my_hash_raw = md5()
    chunk = file.read(8192)
    while chunk:
        my_hash_raw.update(chunk)
        chunk = file.read(8192)

    file_name = "{}.gz".format(my_hash_raw.hexdigest())
    tmp_reference_path = os.path.join("/tmp", "reference", file_name)

    file.seek(0)
    with open(tmp_reference_path, "wb") as output_stream:
        output_stream.write(file.read())

    return my_hash_raw.hexdigest()


@login_required
def finalize_reference(request):
    pass


#########################################################################


@login_required
def reference_details(request, reference_id):

    reference = get_object_or_404(Reference, pk=reference_id)
    form = ReferenceEditForm(instance=reference)

    if request.method == "POST":
        form = ReferenceEditForm(request.POST, instance=reference)

        if form.is_valid():
            form.save()

            return HttpResponseRedirect(reverse("browser:references"))

    context = {"reference": reference, "form": form}

    return render(request, "browser/refrence_details.html", context)


#########################################################################


@login_required
def download_reference(request, reference_id):
    reference = get_object_or_404(Reference, pk=reference_id)
    file_path = reference.reference_file_path

    if os.path.exists(file_path):
        with open(file_path, "rb") as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response["Content-Disposition"] = (
                "inline; filename=" + reference.name + ".fa.gz"
            )
        return response

    raise Http404


#########################################################################


@login_required
def delete_reference(request, reference_id):
    context = dict()

    reference = get_object_or_404(Reference, id=reference_id)
    context = {"reference": reference}

    return render(request, "browser/delete_reference.html", context)


#############################################################################


@login_required
def erase_reference(request, reference_id):
    reference = get_object_or_404(Reference, id=reference_id)
    os.remove(reference.reference_file_path)
    reference.delete()

    return HttpResponseRedirect(reverse("browser:references"))


#############################################################################


def erase_reference(request, error_message):

    context = {"error_message": error_message}
    return render(request, "browser/error_page.html", context)
