from django import forms
from django.forms import ModelForm, formset_factory

from django.forms import formset_factory
from django.forms.widgets import ClearableFileInput, FileInput

from django.contrib.auth.models import User, Group

from django.contrib.auth.forms import UserCreationForm

from django.core.exceptions import ValidationError

from .models import Project, Experiment, Reference

from datetime import datetime

from ribopy import Ribo

from .Fasta import FastaFile


###############################################################################


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description", "public"]


class ProjectDescriptionForm(ModelForm):
    class Meta:
        model = Project
        fields = ["description"]


################################################################################


class RiboUploadForm(forms.Form):
    ribo_file = forms.FileField(widget=ClearableFileInput(attrs={"accept": ".ribo"}))


################################################################################


class NewUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "password1", "password2")

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True

        if commit:
            user.save()
        return user


################################################################################


class UploadRiboFileForm(forms.Form):
    ribo_file = forms.FileField(widget=ClearableFileInput(attrs={"accept": ".ribo"}))
    project_id = forms.CharField(widget=forms.HiddenInput(), required=False)

    def clean_ribo_file(self):
        ribo_file = self.cleaned_data["ribo_file"]
        ribo_file.seek(0)
        try:
            myribo = Ribo(ribo_file)
            number_of_experiments = len(myribo.experiments)
        except:
            raise ValidationError(("Invalid ribo file."), code="invalid")

        if number_of_experiments < 1:
            raise ValidationError(
                ("No experiments found in the ribo file."), code="invalid"
            )

        return ribo_file


################################################################################


class UnitExperimentPickForm(forms.Form):
    selected = forms.BooleanField(label="", required=False)
    experiment = forms.CharField(widget=forms.HiddenInput(), required=False)


ExperimentPickFormSet = formset_factory(UnitExperimentPickForm, extra=0)

################################################################################


class ExperimentDescriptionForm(ModelForm):
    class Meta:
        model = Experiment
        fields = ["description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }
        labels = {"description": ""}


##################################################################################

################################################################################


################################################################################


class ReferenceUploadForm(forms.Form):
    reference_file = forms.FileField(widget=ClearableFileInput(attrs={"accept": ".gz"}))


#################################################################################


class ReferenceForm(ModelForm):
    file_hash = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Reference

        fields = ["name", "organism", "description"]


#################################################################################


class ReferenceEditForm(ModelForm):
    class Meta:
        model = Reference

        fields = ["organism", "description"]


############################################################################


class ExperimentReferenceForm(ModelForm):
    class Meta:
        model = Experiment
        fields = ["reference"]

    def clean_reference(self):
        ribo_handle = Ribo(self.instance.ribo_file_path)
        reference = self.cleaned_data["reference"]

        if not reference:
            """IF reference is none then there is nothing to check."""
            return reference

        reference_fasta = FastaFile(reference.reference_file_path)

        reference_dict = dict()
        for transcript_entry in reference_fasta:
            reference_dict[transcript_entry.header] = len(transcript_entry.sequence)

        ribo_transcripts = ribo_handle.transcript_names
        ribo_lengths = ribo_handle.transcript_lengths

        for this_transcript in ribo_transcripts:
            this_length = ribo_lengths[this_transcript]
            reference_length = reference_dict.get(this_transcript, -1)
            if this_length != reference_length:
                if reference_length == -1:
                    fail_message = "The transcript in the experiment (ribo file) does not exist in reference: {}".format(
                        this_transcript
                    )
                else:
                    fail_message = (
                        "The lengths of the transcript {} do not match {} vs {}".format(
                            this_transcript,
                            this_length,
                            reference_dict.get(this_transcript, -1),
                        )
                    )
                raise ValidationError("Incompatible reference:" + fail_message)

        return reference
