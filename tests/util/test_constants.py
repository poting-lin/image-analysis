from unittest import TestCase
from src.util.constants import validation_error_msg


class ConstantsTestCase(TestCase):
    """Pagination test case"""

    def test_validate_constants(self):
        self.assertGreaterEqual(
            validation_error_msg["err_msg"], "Invalid request, id param is required and should be valid ObjectId.")
