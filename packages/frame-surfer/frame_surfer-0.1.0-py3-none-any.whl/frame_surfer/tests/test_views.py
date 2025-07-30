"""Unit tests for views."""

from nautobot.apps.testing import ViewTestCases

from frame_surfer import models
from frame_surfer.tests import fixtures


class FrameSurferExampleModelViewTest(ViewTestCases.PrimaryObjectViewTestCase):
    # pylint: disable=too-many-ancestors
    """Test the FrameSurferExampleModel views."""

    model = models.FrameSurferExampleModel
    bulk_edit_data = {"description": "Bulk edit views"}
    form_data = {
        "name": "Test 1",
        "description": "Initial model",
    }

    update_data = {
        "name": "Test 2",
        "description": "Updated model",
    }

    @classmethod
    def setUpTestData(cls):
        fixtures.create_framesurferexamplemodel()
