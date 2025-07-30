"""API serializers for frame_surfer."""

from nautobot.apps.api import NautobotModelSerializer, TaggedModelSerializerMixin

from frame_surfer import models


class FrameSurferExampleModelSerializer(NautobotModelSerializer, TaggedModelSerializerMixin):
    """FrameSurferExampleModel Serializer."""

    class Meta:
        model = models.FrameSurferExampleModel
        fields = "__all__"


class FrameSurferPhotoModelSerializer(NautobotModelSerializer, TaggedModelSerializerMixin):
    """PhotoModel Serializer."""

    class Meta:
        model = models.PhotoModel
        fields = "__all__"


class UnsplashModelSerializer(NautobotModelSerializer, TaggedModelSerializerMixin):
    """UnsplashModel Serializer."""

    class Meta:
        model = models.UnsplashModel
        fields = "__all__"


class FrameSurferFrameTVModelSerializer(NautobotModelSerializer, TaggedModelSerializerMixin):
    """FrameSurferFrameTVModel Serializer."""

    class Meta:
        model = models.FrameTV
        fields = "__all__"
        # read_only_fields = []  # Use this to specify any read-only fields
