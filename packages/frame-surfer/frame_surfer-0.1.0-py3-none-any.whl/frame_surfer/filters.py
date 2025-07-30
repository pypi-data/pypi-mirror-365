"""Filtering for frame_surfer."""

from nautobot.apps.filters import NameSearchFilterSet, NautobotFilterSet

from frame_surfer import models


# FRAME SURFER MODEL FILTER SET
class FrameSurferFrameTVModelFilterSet(NameSearchFilterSet, NautobotFilterSet):  # pylint: disable=too-many-ancestors
    """Filter for FrameSurferExampleModel."""

    class Meta:
        """Meta attributes for filter."""

        model = models.FrameTV

        # add any fields from the model that you would like to filter your searches by using those
        fields = "__all__"


# UNSPLASH MODEL FILTER SET
class FrameSurferUnsplashModelFilterSet(NameSearchFilterSet, NautobotFilterSet):
    """Filter for UnsplashModel."""

    class Meta:
        """Meta attributes for filter."""

        model = models.UnsplashModel

        # add any fields from the model that you would like to filter your searches by using those
        fields = "__all__"


# PhotoModel Filter Set
class FrameSurferPhotoModelFilterSet(NameSearchFilterSet, NautobotFilterSet):
    """Filter for PhotoModel."""

    class Meta:
        """Meta attributes for filter."""

        model = models.PhotoModel

        # add any fields from the model that you would like to filter your searches by using those
        fields = "__all__"
