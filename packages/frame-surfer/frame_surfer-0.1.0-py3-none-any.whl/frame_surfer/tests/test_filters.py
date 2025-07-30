"""Test FrameSurferExampleModel Filter."""

from nautobot.apps.testing import FilterTestCases

from frame_surfer import filters, models
from frame_surfer.tests import fixtures


class FrameSurferExampleModelFilterTestCase(FilterTestCases.FilterTestCase):
    """FrameSurferExampleModel Filter Test Case."""

    queryset = models.FrameSurferExampleModel.objects.all()
    filterset = filters.FrameSurferExampleModelFilterSet
    generic_filter_tests = (
        ("id",),
        ("created",),
        ("last_updated",),
        ("name",),
    )

    @classmethod
    def setUpTestData(cls):
        """Setup test data for FrameSurferExampleModel Model."""
        fixtures.create_framesurferexamplemodel()

    def test_q_search_name(self):
        """Test using Q search with name of FrameSurferExampleModel."""
        params = {"q": "Test One"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_q_invalid(self):
        """Test using invalid Q search for FrameSurferExampleModel."""
        params = {"q": "test-five"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)
