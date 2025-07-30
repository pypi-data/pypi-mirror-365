"""Forms for frame_surfer."""

from django import forms
from nautobot.apps.forms import NautobotBulkEditForm, NautobotFilterForm, NautobotModelForm, TagsBulkEditFormMixin

from frame_surfer import models


# Frame TV MODEL FORMS
class FrameSurferFrameTVModelForm(NautobotModelForm):  # pylint: disable=too-many-ancestors
    """FrameSurferExampleModel creation/edit form."""

    class Meta:
        """Meta attributes."""

        model = models.FrameTV
        fields = "__all__"


class FrameSurferFrameTVModelBulkEditForm(TagsBulkEditFormMixin, NautobotBulkEditForm):  # pylint: disable=too-many-ancestors
    """FrameSurferExampleModel bulk edit form."""

    pk = forms.ModelMultipleChoiceField(queryset=models.FrameTV.objects.all(), widget=forms.MultipleHiddenInput)
    description = forms.CharField(required=False)

    class Meta:
        """Meta attributes."""

        nullable_fields = [
            "description",
        ]


class FrameSurferFrameTVModelFilterForm(NautobotFilterForm):
    """Filter form to filter searches."""

    model = models.FrameTV
    field_order = ["q", "name"]

    q = forms.CharField(
        required=False,
        label="Search",
        help_text="Search within Name.",
    )
    name = forms.CharField(required=False, label="Name")


# UNSPLASH MODEL FORMS
class FrameSurferUnsplashModelForm(NautobotModelForm):  # pylint: disable=too-many-ancestors
    """UnsplashModel creation/edit form."""

    class Meta:
        """Meta attributes."""

        model = models.UnsplashModel
        fields = "__all__"


class FrameSurferUnsplashModelBulkEditForm(TagsBulkEditFormMixin, NautobotBulkEditForm):  # pylint: disable=too-many-ancestors
    """UnsplashModel bulk edit form."""

    pk = forms.ModelMultipleChoiceField(queryset=models.UnsplashModel.objects.all(), widget=forms.MultipleHiddenInput)
    name = forms.CharField(required=False)

    class Meta:
        """Meta attributes."""

        nullable_fields = [
            "name",
        ]


class FrameSurferUnsplashModelFilterForm(NautobotFilterForm):
    """Filter form to filter searches."""

    model = models.UnsplashModel
    field_order = ["q", "name"]

    q = forms.CharField(
        required=False,
        label="Search",
        help_text="Search within Name.",
    )
    name = forms.CharField(required=False, label="Name")


# PhotoModel FORMS
class FrameSurferPhotoModelForm(NautobotModelForm):  # pylint: disable=too-many-ancestors
    """PhotoModel creation/edit form."""

    class Meta:
        """Meta attributes."""

        model = models.PhotoModel
        fields = "__all__"


class FrameSurferPhotoModelBulkEditForm(TagsBulkEditFormMixin, NautobotBulkEditForm):  # pylint: disable=too-many-ancestors
    """PhotoModel bulk edit form."""

    pk = forms.ModelMultipleChoiceField(queryset=models.PhotoModel.objects.all(), widget=forms.MultipleHiddenInput)
    name = forms.CharField(required=False)

    class Meta:
        """Meta attributes."""

        nullable_fields = [
            "name",
        ]


class FrameSurferPhotoModelFilterForm(NautobotFilterForm):
    """Filter form to filter searches."""

    model = models.PhotoModel
    field_order = ["q", "name"]

    q = forms.CharField(
        required=False,
        label="Search",
        help_text="Search within Name.",
    )
    name = forms.CharField(required=False, label="Name")
