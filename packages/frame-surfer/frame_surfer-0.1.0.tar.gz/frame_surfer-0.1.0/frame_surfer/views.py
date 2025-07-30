"""Views for frame_surfer."""

from nautobot.apps.views import NautobotUIViewSet

from frame_surfer import filters, forms, models, tables
from frame_surfer.api import serializers


class FrameSurferFrameTVModelUIViewSet(NautobotUIViewSet):
    """ViewSet for FrameSurferFrameTVModel views."""

    bulk_update_form_class = forms.FrameSurferFrameTVModelBulkEditForm
    filterset_class = filters.FrameSurferFrameTVModelFilterSet
    filterset_form_class = forms.FrameSurferFrameTVModelFilterForm
    form_class = forms.FrameSurferFrameTVModelForm
    lookup_field = "pk"
    queryset = models.FrameTV.objects.all()
    serializer_class = serializers.FrameSurferFrameTVModelSerializer
    table_class = tables.FrameSurferFrameTVModelTable


class FrameSurferUnsplashModelUIViewSet(NautobotUIViewSet):
    """ViewSet for FrameSurferUnsplashModel views."""

    bulk_update_form_class = forms.FrameSurferUnsplashModelBulkEditForm
    filterset_class = filters.FrameSurferUnsplashModelFilterSet
    filterset_form_class = forms.FrameSurferUnsplashModelFilterForm
    form_class = forms.FrameSurferUnsplashModelForm
    lookup_field = "pk"
    queryset = models.UnsplashModel.objects.all()
    serializer_class = serializers.UnsplashModelSerializer
    table_class = tables.FrameSurferUnsplashModelTable


class FrameSurferPhotoModelUIViewSet(NautobotUIViewSet):
    """ViewSet for FrameSurferPhotoModel views."""

    bulk_update_form_class = forms.FrameSurferPhotoModelBulkEditForm
    filterset_class = filters.FrameSurferPhotoModelFilterSet
    filterset_form_class = forms.FrameSurferPhotoModelFilterForm
    form_class = forms.FrameSurferPhotoModelForm
    lookup_field = "pk"
    queryset = models.PhotoModel.objects.all()
    serializer_class = serializers.FrameSurferPhotoModelSerializer
    table_class = tables.FrameSurferPhotoModelTable
    context_object_name = "photo_model"
