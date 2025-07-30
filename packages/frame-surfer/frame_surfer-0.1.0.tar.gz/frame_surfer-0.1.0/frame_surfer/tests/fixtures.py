"""Create fixtures for tests."""

from frame_surfer.models import FrameSurferExampleModel


def create_framesurferexamplemodel():
    """Fixture to create necessary number of FrameSurferExampleModel for tests."""
    FrameSurferExampleModel.objects.create(name="Test One")
    FrameSurferExampleModel.objects.create(name="Test Two")
    FrameSurferExampleModel.objects.create(name="Test Three")
