"""Test framesurferexamplemodel forms."""

from django.test import TestCase

from frame_surfer import forms


class FrameSurferExampleModelTest(TestCase):
    """Test FrameSurferExampleModel forms."""

    def test_specifying_all_fields_success(self):
        form = forms.FrameSurferExampleModelForm(
            data={
                "name": "Development",
                "description": "Development Testing",
            }
        )
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())

    def test_specifying_only_required_success(self):
        form = forms.FrameSurferExampleModelForm(
            data={
                "name": "Development",
            }
        )
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())

    def test_validate_name_framesurferexamplemodel_is_required(self):
        form = forms.FrameSurferExampleModelForm(data={"description": "Development Testing"})
        self.assertFalse(form.is_valid())
        self.assertIn("This field is required.", form.errors["name"])
