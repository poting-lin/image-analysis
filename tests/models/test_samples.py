from unittest import TestCase

import uuid
from pydantic import ValidationError

from src.models.samples import SamplesRequestModel


class SamplesRequestModelTestCases(TestCase):
    def setUp(self):
        # mock OpMId and SpaceId as string in UUID format
        # the same type and format as uniqueidentifier in SQL database
        self.mock_name = "sample 123"
        self.mock_invalid_name = "abc_ew'"
        self.mock_owner = "mock owner"
        self.inventory_number = "A123-998 EFC"

    def test_samples_request_model(self):
        # arrange
        expect_mock_object = {
            "name": self.mock_name,
            "owner": self.mock_owner,
            "inventoryNumber": self.inventory_number,
            "sampleId": None
        }

        # act
        response = SamplesRequestModel(
            **expect_mock_object)
        # assert
        self.assertEqual(response.dict(), expect_mock_object)

    def test_samples_request_model_invalid_dataset(self):
        # arrange
        expect_mock_object = {
            "name": self.mock_invalid_name,
            "owner": self.mock_owner,
            "inventoryNumber": self.inventory_number,
            "sampleId": None
        }

        # act
        try:
            SamplesRequestModel(
                **expect_mock_object)
        except ValidationError as exception:
            # assert
            self.assertIn(
                "do not match pattern, it allows only letters, umlaut, umbers and special characters", str(exception))

    def test_samples_request_model_unexpected_column(self):
        # arrange
        expect_mock_object = {
            "name": self.mock_name,
            "owner": self.mock_owner,
            "inventoryNumber": self.inventory_number,
            "sampleId": None,
            "unexpected_column": "value"
        }

        # act
        response = SamplesRequestModel(
            **expect_mock_object)
        # assert
        del expect_mock_object["unexpected_column"]
        self.assertEqual(response.dict(), expect_mock_object)
