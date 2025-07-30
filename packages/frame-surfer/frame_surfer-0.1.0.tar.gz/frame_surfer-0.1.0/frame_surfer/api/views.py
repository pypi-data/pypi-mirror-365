"""API views for frame_surfer."""

from nautobot.apps.api import NautobotModelViewSet

from frame_surfer import filters, models
from frame_surfer.api import serializers


class FrameSurferFrameTVModelViewSet(NautobotModelViewSet):  # pylint: disable=too-many-ancestors
    """FrameSurferExampleModel viewset."""

    queryset = models.FrameTV.objects.all()
    serializer_class = serializers.FrameSurferFrameTVModelSerializer
    filterset_class = filters.FrameSurferFrameTVModelFilterSet

    # Option for modifying the default HTTP methods:
    # http_method_names = ["get", "post", "put", "patch", "delete", "head", "options", "trace"]


class FrameSurferUnsplashModelViewSet(NautobotModelViewSet):  # pylint: disable=too-many-ancestors
    """UnsplashModel viewset."""

    queryset = models.UnsplashModel.objects.all()
    serializer_class = serializers.UnsplashModelSerializer
    filterset_class = filters.FrameSurferUnsplashModelFilterSet

    # Option for modifying the default HTTP methods:
    # http_method_names = ["get", "post", "put", "patch", "delete", "head", "options", "trace"]


class FrameSurferPhotoModelViewSet(NautobotModelViewSet):  # pylint: disable=too-many-ancestors
    """PhotoModel viewset."""

    queryset = models.PhotoModel.objects.all()
    serializer_class = serializers.FrameSurferPhotoModelSerializer
    filterset_class = filters.FrameSurferPhotoModelFilterSet

    # Option for modifying the default HTTP methods:
    # http_method_names = ["get", "post", "put", "patch", "delete", "head", "options", "trace"]
