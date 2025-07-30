"""App declaration for frame_surfer."""

# Metadata is inherited from Nautobot. If not including Nautobot in the environment, this should be added
from importlib import metadata

from nautobot.apps import NautobotAppConfig

__version__ = metadata.version(__name__)


class FrameSurferConfig(NautobotAppConfig):
    """App configuration for the frame_surfer app."""

    name = "frame_surfer"
    verbose_name = "Frame Surfer"
    version = __version__
    author = "Angelo Poggi"
    description = "Frame Surfer."
    base_url = "frame-surfer"
    required_settings = []
    min_version = "2.0.0"
    max_version = "2.9999"
    default_settings = {}
    caching_config = {}
    docs_view_name = "plugins:frame_surfer:docs"


config = FrameSurferConfig  # pylint:disable=invalid-name
