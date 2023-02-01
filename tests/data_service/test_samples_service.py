from unittest import TestCase
from unittest.mock import Mock, patch

from datetime import datetime
import calendar
import uuid
from pydantic import ValidationError

from src.models.samples import SamplesRequestModel
from src.data_service.samples_service import SamplesService


class SamplesTestCases(TestCase):
    def setUp(self):
        self.tid = "f112abc4-d49a-4bc9-a058-ddbe2c0bd2ab"
        self.uid = "7b429f8b-ce49-4e34-9185-e8f71f51255"
        self._samples_service = SamplesService(self.tid, self.uid)
        current_datetime = datetime.utcnow()
        current_timetuple = current_datetime.utctimetuple()
        current_timestamp = calendar.timegm(current_timetuple)
        self.new_sample_name = f"test sample entity - {current_timestamp}"
        self.inventory_number = f"inventory Number - {str(uuid.uuid4())}"
        self.owner = "test owner"

    def tearDown(self):
        pass

    @patch('src.services.mongodb.MongoDBService.find_documents')
    def test_find_by_name_and_inventory_number(self, mock_find_documents):
        # arrange
        mock_name = "test"
        mock_inventory_number = "a1566b11-a3b2-48cc-9ea7-0eba242eb7ad2"
        mock_document_list = [
            {
                "sampleId": "3b23dfd5-ee3a-4bbc-8c15-ab6d0c188d8c",
                "name": mock_name,
                "owner": "test",
                "inventoryNumber": mock_inventory_number,
                "createdAt": "2022-11-13 11:48:29",
                "lastUpdatedAt": "2022-11-13 12:06:03"
            }
        ]

        mock_find_documents.return_value = Mock()
        mock_find_documents.return_value = mock_document_list

        # act
        response = self._samples_service.find_by_name_and_inventory_number(
            mock_name, mock_inventory_number)
        self.assertEqual(response[0]["inventoryNumber"], mock_inventory_number)

    @patch('src.services.mongodb.MongoDBService.find_documents')
    def test_find_by_name_and_inventory_number_no_document(self, mock_find_documents):
        # it should return a empty list if no document found
        # arrange
        mock_name = "test"
        mock_inventory_number = "a1566b11-a3b2-48cc-9ea7-0eba242eb7ad2"

        mock_find_documents.return_value = Mock()
        mock_find_documents.return_value = []

        # act
        response = self._samples_service.find_by_name_and_inventory_number(
            mock_name, mock_inventory_number)
        self.assertEqual(len(response), 0)

    @patch('src.services.mongodb.MongoDBService.find_documents')
    def test_find_by_inventory_number(self, mock_find_documents):
        # arrange
        mock_name = "test"
        mock_inventory_number = "a1566b11-a3b2-48cc-9ea7-0eba242eb7ad2"
        mock_document_list = [
            {
                "sampleId": "3b23dfd5-ee3a-4bbc-8c15-ab6d0c188d8c",
                "name": mock_name,
                "owner": "test",
                "inventoryNumber": mock_inventory_number,
                "createdAt": "2022-11-13 11:48:29",
                "lastUpdatedAt": "2022-11-13 12:06:03"
            }
        ]

        mock_find_documents.return_value = Mock()
        mock_find_documents.return_value = mock_document_list

        # act
        response = self._samples_service.find_by_inventory_number(
            mock_inventory_number)
        self.assertEqual(response[0]["inventoryNumber"], mock_inventory_number)

    @patch('src.services.mongodb.MongoDBService.find_documents')
    def test_find_by_inventory_number_no_document(self, mock_find_documents):
        # it should return a empty list if no document found
        # arrange
        mock_name = "test"
        mock_inventory_number = "a1566b11-a3b2-48cc-9ea7-0eba242eb7ad2"

        mock_find_documents.return_value = Mock()
        mock_find_documents.return_value = []

        # act
        response = self._samples_service.find_by_inventory_number(
            mock_inventory_number)
        self.assertEqual(len(response), 0)

    def test_insert_and_delete(self):
        # definition of duplicated: combination of name and inventory number

        # create a new sample
        sample = SamplesRequestModel(
            name=self.new_sample_name,
            owner=self.owner,
            inventoryNumber=self.inventory_number
        )
        response = self._samples_service.insert(sample)

        self.assertEqual(len(response), 6)
        self.assertEqual(response["name"], self.new_sample_name)

        # remove testing entity
        sample_id = response["sampleId"]
        response = self._samples_service.delete(sample_id)
        self.assertEqual(response, True)

    def test_insert_with_emoji(self):
        # create a new sample
        name_with_emoji = f"test😁"

        try:
            SamplesRequestModel(
                name=name_with_emoji,
                owner=self.owner,
                inventoryNumber=self.inventory_number
            )
        except ValidationError as exception:
            self.assertIn(
                "do not match pattern, it allows only letters, umlaut, umbers and special characters", str(exception))

    def test_insert_with_the_same_existing_content_and_delete(self):
        # create a new content with a existing name and inventory number should return false

        existing_name = f"{self.new_sample_name} - existing"
        existing_inventory_number = f"{self.inventory_number} - existing"
        existing_sample = SamplesRequestModel(
            name=existing_name,
            owner=self.owner,
            inventoryNumber=existing_inventory_number
        )
        response = self._samples_service.insert(existing_sample)

        self.assertEqual(len(response), 6)
        self.assertEqual(response["name"], existing_name)
        self.assertEqual(response["owner"], self.owner)
        self.assertEqual(response["inventoryNumber"],
                         existing_inventory_number)

        new_sample = SamplesRequestModel(
            name=existing_name,
            owner=self.owner,
            inventoryNumber=existing_inventory_number
        )
        try:
            self._samples_service.insert(new_sample)
        except ValueError as exception:
            self.assertIn("Validation error", str(exception))
        finally:
            sample_id = response["sampleId"]
            response = self._samples_service.delete(sample_id)
            self.assertEqual(response, True)

    def test_update_create_update_same_content_and_delete(self):
        # create a new sample and update with the same name and inventory number should return true
        sample = SamplesRequestModel(
            name=self.new_sample_name,
            owner=self.owner,
            inventoryNumber=self.inventory_number
        )
        response = self._samples_service.insert(sample)

        self.assertEqual(len(response), 6)
        self.assertEqual(response["name"], self.new_sample_name)
        self.assertEqual(response["owner"], self.owner)
        self.assertEqual(response["inventoryNumber"], self.inventory_number)

        sample_id = response["sampleId"]

        response = self._samples_service.update(sample_id, sample)
        self.assertEqual(response["name"], self.new_sample_name)
        self.assertEqual(response["owner"], self.owner)
        self.assertEqual(response["inventoryNumber"], self.inventory_number)

        sample_id = response["sampleId"]
        response = self._samples_service.delete(sample_id)
        self.assertEqual(response, True)

    def test_update_create_update_new_name_and_delete(self):
        # create a new sample and update with a new name should return true
        sample = SamplesRequestModel(
            name=self.new_sample_name,
            owner=self.owner,
            inventoryNumber=self.inventory_number
        )
        response = self._samples_service.insert(sample)

        self.assertEqual(len(response), 6)
        self.assertEqual(response["name"], self.new_sample_name)
        self.assertEqual(response["owner"], self.owner)
        self.assertEqual(response["inventoryNumber"], self.inventory_number)

        sample_id = response["sampleId"]

        new_name = f"{self.new_sample_name} - updated"
        new_sample = SamplesRequestModel(
            name=new_name,
            owner=self.owner,
            inventoryNumber=self.inventory_number
        )

        response = self._samples_service.update(
            sample_id, new_sample)
        self.assertEqual(response["name"], new_name)
        self.assertEqual(response["owner"], self.owner)
        self.assertEqual(response["inventoryNumber"], self.inventory_number)

        sample_id = response["sampleId"]
        response = self._samples_service.delete(sample_id)
        self.assertEqual(response, True)

    def test_update_create_update_new_inventory_number_and_delete(self):
        # create a new sample and update with a new inventory number should return true
        sample = SamplesRequestModel(
            name=self.new_sample_name,
            owner=self.owner,
            inventoryNumber=self.inventory_number
        )
        response = self._samples_service.insert(sample)

        self.assertEqual(len(response), 6)
        self.assertEqual(response["name"], self.new_sample_name)
        self.assertEqual(response["owner"], self.owner)
        self.assertEqual(response["inventoryNumber"], self.inventory_number)

        sample_id = response["sampleId"]

        new_inventory_number = f"{self.inventory_number} - updated"
        new_sample = SamplesRequestModel(
            name=self.new_sample_name,
            owner=self.owner,
            inventoryNumber=new_inventory_number
        )

        response = self._samples_service.update(
            sample_id, new_sample)
        self.assertEqual(response["name"], self.new_sample_name)
        self.assertEqual(response["owner"], self.owner)
        self.assertEqual(response["inventoryNumber"], new_inventory_number)

        sample_id = response["sampleId"]
        response = self._samples_service.delete(sample_id)
        self.assertEqual(response, True)

    def test_update_create_update_existing_content_and_delete(self):
        # create a new sample and update with a existing name and inventory number should return false

        existing_name = f"{self.new_sample_name} - existing"
        existing_inventory_number = f"{self.inventory_number} - existing"
        existing_sample = SamplesRequestModel(
            name=existing_name,
            owner=self.owner,
            inventoryNumber=existing_inventory_number
        )
        response = self._samples_service.insert(existing_sample)

        self.assertEqual(len(response), 6)
        self.assertEqual(response["name"], existing_name)
        self.assertEqual(response["owner"], self.owner)
        self.assertEqual(response["inventoryNumber"],
                         existing_inventory_number)
        existing_sample_id = response["sampleId"]

        new_name = f"{self.new_sample_name} - new"
        new_inventory_number = f"{self.inventory_number} - new"
        new_sample = SamplesRequestModel(
            name=new_name,
            owner=self.owner,
            inventoryNumber=new_inventory_number
        )
        response = self._samples_service.insert(new_sample)

        self.assertEqual(len(response), 6)
        self.assertEqual(response["name"], new_name)
        self.assertEqual(response["owner"], self.owner)
        self.assertEqual(response["inventoryNumber"], new_inventory_number)

        new_sample_id = response["sampleId"]

        #  update the new sample entity with existing name and inventory number
        updated_sample_name = existing_name
        updated_inventory_number = existing_inventory_number
        updated_sample = SamplesRequestModel(
            name=updated_sample_name,
            owner=self.owner,
            inventoryNumber=updated_inventory_number
        )

        try:
            self._samples_service.update(
                new_sample_id, updated_sample)
        except ValueError as exception:
            self.assertIn("Validation error", str(exception))
        finally:
            response = self._samples_service.delete(existing_sample_id)
            self.assertEqual(response, True)
            response = self._samples_service.delete(new_sample_id)
            self.assertEqual(response, True)
