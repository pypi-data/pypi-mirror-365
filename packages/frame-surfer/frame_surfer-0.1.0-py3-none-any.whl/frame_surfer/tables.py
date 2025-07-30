"""Tables for frame_surfer."""

import django_tables2 as tables
from nautobot.apps.tables import BaseTable, ButtonsColumn, ToggleColumn

from frame_surfer import models


class FrameSurferFrameTVModelTable(BaseTable):
    # pylint: disable=R0903
    """Table for list view."""

    pk = ToggleColumn()
    name = tables.Column(linkify=True)
    actions = ButtonsColumn(
        models.FrameTV,
        # Option for modifying the default action buttons on each row:
        # buttons=("changelog", "edit", "delete"),
        # Option for modifying the pk for the action buttons:
        pk_field="pk",
    )

    class Meta(BaseTable.Meta):
        """Meta attributes."""

        model = models.FrameTV
        fields = (
            "pk",
            "name",
            "description",
            "api_service",
            "ip_address",
        )

        # Option for modifying the columns that show up in the list view by default:
        # default_columns = (
        #     "pk",
        #     "name",
        #     "description",
        # )


class FrameSurferUnsplashModelTable(BaseTable):
    """Table for UnsplashModel list view."""

    pk = ToggleColumn()
    name = tables.Column(linkify=True)
    actions = ButtonsColumn(
        models.UnsplashModel,
        # Option for modifying the default action buttons on each row:
        # buttons=("changelog", "edit", "delete"),
        # Option for modifying the pk for the action buttons:
        pk_field="pk",
    )

    class Meta(BaseTable.Meta):
        """Meta attributes."""

        model = models.UnsplashModel
        fields = (
            "pk",
            "name",
        )


class FrameSurferPhotoModelTable(BaseTable):
    """Table for PhotoModel list view."""

    pk = ToggleColumn()
    name = tables.Column(linkify=False)
    actions = ButtonsColumn(
        models.PhotoModel,
        # Option for modifying the default action buttons on each row:
        # buttons=("changelog", "edit", "delete"),
        # Option for modifying the pk for the action buttons:
        pk_field="pk",
    )

    class Meta(BaseTable.Meta):
        """Meta attributes."""

        model = models.PhotoModel
        fields = (
            "pk",
            "name",
            "url",
            "downloaded_at",
            "tv",
            "tv_file_name",
        )
