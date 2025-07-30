"""Models for Frame Surfer."""

# Django imports
from django.db import models

# Nautobot imports
from nautobot.apps.models import PrimaryModel, extras_features
from nautobot.extras.models import SecretsGroup


# If you want to choose a specific model to overload in your class declaration, please reference the following documentation:
# how to chose a database model: https://docs.nautobot.com/projects/core/en/stable/plugins/development/#database-models
# If you want to use the extras_features decorator please reference the following documentation
# https://docs.nautobot.com/projects/core/en/stable/development/core/model-checklist/#extras-features
@extras_features("custom_links", "custom_validators", "export_templates", "graphql", "webhooks")
class FrameSurferExampleModel(PrimaryModel):  # pylint: disable=too-many-ancestors
    """Base model for Frame Surfer app."""

    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=200, blank=True)
    # additional model fields

    class Meta:
        """Meta class."""

        ordering = ["name"]

        # Option for fixing capitalization (i.e. "Snmp" vs "SNMP")
        # verbose_name = "Frame Surfer"

        # Option for fixing plural name (i.e. "Chicken Tenders" vs "Chicken Tendies")
        # verbose_name_plural = "Frame Surfers"

    def __str__(self):
        """Stringify instance."""
        return self.name


@extras_features("custom_links", "custom_validators", "export_templates", "graphql", "webhooks")
class UnsplashModel(PrimaryModel):
    name = models.CharField(max_length=256, unique=True)
    url = models.URLField()
    access_key = models.ForeignKey(
        SecretsGroup, on_delete=models.PROTECT, related_name="access_token", blank=True, null=True
    )

    def __str__(self):
        return self.name


@extras_features("custom_links", "custom_validators", "export_templates", "graphql", "webhooks")
class FrameTV(PrimaryModel):
    name = models.CharField(max_length=256, unique=True)
    ip_address = models.GenericIPAddressField(protocol="both", blank=True, null=True)
    api_service = models.ForeignKey(UnsplashModel, on_delete=models.CASCADE, related_name="api_service")
    topics = models.TextField(help_text="Comma-sperated list of topcis", blank=True, null=True)
    matte_options = models.CharField(max_length=256, blank=True)

    class Meta:
        """Meta class."""

        ordering = ["name"]

    def __str__(self):
        return self.name


@extras_features("custom_links", "custom_validators", "export_templates", "graphql", "webhooks")
class PhotoModel(PrimaryModel):
    name = models.CharField(max_length=256, unique=True)
    downloaded_at = models.DateTimeField(auto_now=True)
    thumbnail = models.CharField(max_length=512, blank=True, null=True, help_text="Path to thumbnail image")
    url = models.CharField(max_length=512, help_text="URL to the original photo")
    tv = models.ForeignKey(FrameTV, on_delete=models.CASCADE, related_name="photos")
    tv_file_name = models.CharField(max_length=512, blank=True, null=True, help_text="Path to the file on the TV")

    class Meta:
        """Meta class."""

        ordering = ["name"]

    def __str__(self):
        return self.name
