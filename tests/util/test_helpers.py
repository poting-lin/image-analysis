from unittest import TestCase
import uuid
from src.util import helpers


class HelpersTestCase(TestCase):
    """Helper Resolver test case"""

    def setUp(self):
        """Set up dependencies"""
        self.valid_uuid = str(uuid.uuid4())
        self.valid_string = "1234-1324-1234"
        self.valid_number = 1234
        self.valid_float = 123.333

    def test_is_valid_uuid(self):
        self.assertTrue(helpers.is_valid_uuid(self.valid_uuid))
        self.assertFalse(helpers.is_valid_uuid(self.valid_string))
        self.assertFalse(helpers.is_valid_uuid(self.valid_number))

    def test_is_valid_int(self):
        self.assertFalse(helpers.is_int(self.valid_uuid))
        self.assertFalse(helpers.is_int(self.valid_string))
        self.assertTrue(helpers.is_int(self.valid_number))
        self.assertFalse(helpers.is_int(self.valid_float))
