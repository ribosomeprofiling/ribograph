from django.db import models
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError

import re


##################################################################


def validate_name(name):
    m = re.match(r"^[0-9a-zA-Z\-\_ ]*$", name)
    if not m:
        raise (ValidationError("Use only characters, nubers, - and _ in the name."))


##################################################################


class RiboGraphModel(models.Model):
    """
    Derive All Models in the system from this Model
    """

    class Meta:
        abstract = True

    ### Automatically add the creation date of the object
    creation_date = models.DateTimeField(auto_now_add=True)

    ### To take notes for ourselves
    description = models.TextField(blank=True)

    name = models.CharField(
        max_length=150, unique=True, blank=False, validators=[validate_name]
    )

    def __str__(self):
        return self.name


##################################################################


class Project(RiboGraphModel):
    public = models.BooleanField(
        default=False, help_text="Is this item publicly available?"
    )

    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, help_text="Owner of the project."
    )


##################################################################


class Reference(RiboGraphModel):
    reference_file_path = models.TextField(
        unique=False, blank=False, help_text="Path to the sequence file."
    )

    organism = models.CharField(
        max_length=150,
        unique=False,
        blank=True,
        help_text="(Optional) Organism of the reference.",
    )

    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, help_text="Owner of the Reference."
    )


##################################################################


class Experiment(RiboGraphModel):

    name = models.CharField(
        max_length=150, unique=False, blank=False, validators=[validate_name]
    )

    ribo_file_path = models.TextField(
        unique=False, blank=False, help_text="Path to the ribo file in the system."
    )

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, help_text="Owner of the project."
    )

    reference = models.ForeignKey(
        Reference,
        models.SET_NULL,
        blank=True,
        null=True,
        help_text="(Optional) Reference sequences in coverage plots are obtained accordingly.",
    )

    reference_digest = models.CharField(max_length=50, unique=False, blank=True)

    transcript_regex = models.TextField(
        unique=False,
        blank=True,
        help_text="If exists, this regular expression is used to shorten / modify transcript names for easier browsing.",
    )

    class Meta:
        unique_together = (
            "name",
            "project",
        )


##################################################################
