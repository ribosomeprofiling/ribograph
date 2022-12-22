from django import template
from django.urls import reverse
from django_tables2.utils import A

import django_tables2 as tables

from .models import Project, Experiment, Reference


###########################################################################


class ProjectTable(tables.Table):
    name = tables.LinkColumn(
        "browser:project_details",
        verbose_name="Project",
        text=lambda record: record.name,
        args=[A("id")],
    )

    class Meta:
        model = Project
        template_name = "django_tables2/bootstrap-responsive.html"
        attrs = {
            "class": "table table-striped table-bordered table-sm table-hover",
            "id": "dtBasicExample",
            "thead": {"bgcolor": "#c4dcff"},
            "th": {"class": "th-sm"},
        }
        fields = ("name",)


###########################################################################


class ExperimentTable(tables.Table):
    name = tables.LinkColumn(
        "browser:experiment_details",
        verbose_name="experiment",
        text=lambda record: record.name,
        args=[A("id")],
    )

    class Meta:
        model = Experiment
        template_name = "django_tables2/bootstrap-responsive.html"
        attrs = {
            "class": "table table-striped table-bordered table-sm table-hover",
            "id": "dtBasicExample",
            "thead": {"class": "table-primary"},
            "th": {"class": "th-sm"},
        }
        fields = ("name",)


###########################################################################


class ReferenceTable(tables.Table):
    name = tables.LinkColumn(
        "browser:reference_details",
        verbose_name="Reference",
        text=lambda record: record.name,
        args=[A("id")],
    )

    class Meta:
        model = Reference
        template_name = "django_tables2/bootstrap-responsive.html"
        attrs = {
            "class": "table table-striped table-bordered table-sm table-hover",
            "id": "dtBasicExample",
            "thead": {"class": "table-primary"},
            "th": {"class": "th-sm"},
        }
        fields = ("name", "organism")
