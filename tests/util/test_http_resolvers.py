from unittest import TestCase
import uuid
import json
from src.util.http_resolvers import BaseResponse


class HttpResolverTestCase(TestCase):
    """Http resolver Resolver test case"""

    def setUp(self):
        """Set up dependencies"""
        self.valid_uuid = str(uuid.uuid4())
        self.valid_string = "1234-1324-1234"
        self.valid_number = 1234
        self.valid_float = 123.333
        self._base_response = BaseResponse

    def test_is_valid_succeed(self):
        # arrange
        mock_message = "mock message"
        mock_data = "mock data"

        # act
        response = self._base_response.succeed(mock_message, 200, mock_data)
        response_message = json.loads(response.body)["message"]
        response_status_code = json.loads(response.body)["statusCode"]
        response_data = json.loads(response.body)["data"]

        # assert
        self.assertEqual(response_message, mock_message)
        self.assertEqual(response_status_code, 200)
        self.assertEqual(response_data, mock_data)

    def test_is_valid_error(self):
        # arrange
        mock_message = "mock message"
        mock_data = "mock data"

        # act
        response = self._base_response.error(mock_message, 400)
        response_message = json.loads(response.body)["message"]
        response_status_code = json.loads(response.body)["statusCode"]

        # assert
        self.assertEqual(response_message, mock_message)
        self.assertEqual(response_status_code, 400)
