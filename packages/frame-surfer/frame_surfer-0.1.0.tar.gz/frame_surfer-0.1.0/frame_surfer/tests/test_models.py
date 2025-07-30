"""Test FrameSurferExampleModel."""

from nautobot.apps.testing import ModelTestCases

from frame_surfer import models
from frame_surfer.tests import fixtures


class TestFrameSurferExampleModel(ModelTestCases.BaseModelTestCase):
    """Test FrameSurferExampleModel."""

    model = models.FrameSurferExampleModel

    @classmethod
    def setUpTestData(cls):
        """Create test data for FrameSurferExampleModel Model."""
        super().setUpTestData()
        # Create 3 objects for the model test cases.
        fixtures.create_framesurferexamplemodel()

    def test_create_framesurferexamplemodel_only_required(self):
        """Create with only required fields, and validate null description and __str__."""
        framesurferexamplemodel = models.FrameSurferExampleModel.objects.create(name="Development")
        self.assertEqual(framesurferexamplemodel.name, "Development")
        self.assertEqual(framesurferexamplemodel.description, "")
        self.assertEqual(str(framesurferexamplemodel), "Development")

    def test_create_framesurferexamplemodel_all_fields_success(self):
        """Create FrameSurferExampleModel with all fields."""
        framesurferexamplemodel = models.FrameSurferExampleModel.objects.create(
            name="Development", description="Development Test"
        )
        self.assertEqual(framesurferexamplemodel.name, "Development")
        self.assertEqual(framesurferexamplemodel.description, "Development Test")
