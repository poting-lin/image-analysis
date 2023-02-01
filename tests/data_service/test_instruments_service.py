from unittest import TestCase
from unittest.mock import Mock, patch

from datetime import datetime
import calendar
import uuid
from pydantic import ValidationError

from src.models.instruments import InstrumentsRequestModel
from src.data_service.instruments_service import InstrumentsService


class InstrumentsTestCases(TestCase):
    def setUp(self):
        self.tid = "f112abc4-d49a-4bc9-a058-ddbe2c0bd2ab"
        self.uid = "7b429f8b-ce49-4e34-9185-e8f71f51255"
        self._instruments_service = InstrumentsService(self.tid, self.uid)
        current_datetime = datetime.utcnow()
        current_timetuple = current_datetime.utctimetuple()
        current_timestamp = calendar.timegm(current_timetuple)
        self.new_instrument_name = f"test instrument entity - {current_timestamp}"
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
                "instrumentId": "3b23dfd5-ee3a-4bbc-8c15-ab6d0c188d8c",
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
        response = self._instruments_service.find_by_name_and_inventory_number(
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
        response = self._instruments_service.find_by_name_and_inventory_number(
            mock_name, mock_inventory_number)
        self.assertEqual(len(response), 0)

    @patch('src.services.mongodb.MongoDBService.find_documents')
    def test_find_by_inventory_number(self, mock_find_documents):
        # arrange
        mock_name = "test"
        mock_inventory_number = "a1566b11-a3b2-48cc-9ea7-0eba242eb7ad2"
        mock_document_list = [
            {
                "instrumentId": "3b23dfd5-ee3a-4bbc-8c15-ab6d0c188d8c",
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
        response = self._instruments_service.find_by_inventory_number(
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
        response = self._instruments_service.find_by_inventory_number(
            mock_inventory_number)
        self.assertEqual(len(response), 0)

    def test_insert_and_delete(self):
        # definition of duplicated: combination of name and inventory number

        # create a new instrument
        instrument = InstrumentsRequestModel(
            name=self.new_instrument_name,
            owner=self.owner,
            inventoryNumber=self.inventory_number
        )
        response = self._instruments_service.insert(instrument)

        self.assertEqual(len(response), 6)
        self.assertEqual(response["name"], self.new_instrument_name)

        # remove testing entity
        instrument_id = response["instrumentId"]
        response = self._instruments_service.delete(instrument_id)
        self.assertEqual(response, True)

    def test_insert_with_emoji(self):
        # create a new instrument
        name_with_emoji = f"test😁"

        try:
            InstrumentsRequestModel(
                name=name_with_emoji,
                owner=self.owner,
                inventoryNumber=self.inventory_number
            )
        except ValidationError as exception:
            self.assertIn(
                "do not match pattern, it allows only letters, umlaut, umbers and special characters", str(exception))

    def test_insert_with_special_letters(self):
        # create a new instrument
        name_with_special_letters = f"test°§$"
        instrument = InstrumentsRequestModel(
            name=name_with_special_letters,
            owner=self.owner,
            inventoryNumber=self.inventory_number
        )
        response = self._instruments_service.insert(instrument)

        self.assertEqual(len(response), 6)
        self.assertEqual(response["name"], name_with_special_letters)

        # remove testing entity
        instrument_id = response["instrumentId"]
        response = self._instruments_service.delete(instrument_id)
        self.assertEqual(response, True)

    def test_insert_with_the_same_existing_content_and_delete(self):
        # create a new content with a existing name and inventory number should return false

        existing_name = f"{self.new_instrument_name} - existing"
        existing_inventory_number = f"{self.inventory_number} - existing"
        existing_instrument = InstrumentsRequestModel(
            name=existing_name,
            owner=self.owner,
            inventoryNumber=existing_inventory_number
        )
        response = self._instruments_service.insert(existing_instrument)

        self.assertEqual(len(response), 6)
        self.assertEqual(response["name"], existing_name)
        self.assertEqual(response["owner"], self.owner)
        self.assertEqual(response["inventoryNumber"],
                         existing_inventory_number)

        new_instrument = InstrumentsRequestModel(
            name=existing_name,
            owner=self.owner,
            inventoryNumber=existing_inventory_number
        )
        try:
            self._instruments_service.insert(new_instrument)
        except ValueError as exception:
            self.assertIn("Validation error", str(exception))
        finally:
            instrument_id = response["instrumentId"]
            response = self._instruments_service.delete(instrument_id)
            self.assertEqual(response, True)

    def test_update_create_update_same_content_and_delete(self):
        # create a new instrument and update with the same name and inventory number should return true
        instrument = InstrumentsRequestModel(
            name=self.new_instrument_name,
            owner=self.owner,
            inventoryNumber=self.inventory_number
        )
        response = self._instruments_service.insert(instrument)

        self.assertEqual(len(response), 6)
        self.assertEqual(response["name"], self.new_instrument_name)
        self.assertEqual(response["owner"], self.owner)
        self.assertEqual(response["inventoryNumber"], self.inventory_number)

        instrument_id = response["instrumentId"]

        response = self._instruments_service.update(instrument_id, instrument)
        self.assertEqual(response["name"], self.new_instrument_name)
        self.assertEqual(response["owner"], self.owner)
        self.assertEqual(response["inventoryNumber"], self.inventory_number)

        instrument_id = response["instrumentId"]
        response = self._instruments_service.delete(instrument_id)
        self.assertEqual(response, True)

    def test_update_create_update_new_name_and_delete(self):
        # create a new instrument and update with a new name should return true
        instrument = InstrumentsRequestModel(
            name=self.new_instrument_name,
            owner=self.owner,
            inventoryNumber=self.inventory_number
        )
        response = self._instruments_service.insert(instrument)

        self.assertEqual(len(response), 6)
        self.assertEqual(response["name"], self.new_instrument_name)
        self.assertEqual(response["owner"], self.owner)
        self.assertEqual(response["inventoryNumber"], self.inventory_number)

        instrument_id = response["instrumentId"]

        new_name = f"{self.new_instrument_name} - updated"
        new_instrument = InstrumentsRequestModel(
            name=new_name,
            owner=self.owner,
            inventoryNumber=self.inventory_number
        )

        response = self._instruments_service.update(
            instrument_id, new_instrument)
        self.assertEqual(response["name"], new_name)
        self.assertEqual(response["owner"], self.owner)
        self.assertEqual(response["inventoryNumber"], self.inventory_number)

        instrument_id = response["instrumentId"]
        response = self._instruments_service.delete(instrument_id)
        self.assertEqual(response, True)

    def test_update_create_update_new_inventory_number_and_delete(self):
        # create a new instrument and update with a new inventory number should return true
        instrument = InstrumentsRequestModel(
            name=self.new_instrument_name,
            owner=self.owner,
            inventoryNumber=self.inventory_number
        )
        response = self._instruments_service.insert(instrument)

        self.assertEqual(len(response), 6)
        self.assertEqual(response["name"], self.new_instrument_name)
        self.assertEqual(response["owner"], self.owner)
        self.assertEqual(response["inventoryNumber"], self.inventory_number)

        instrument_id = response["instrumentId"]

        new_inventory_number = f"{self.inventory_number} - updated"
        new_instrument = InstrumentsRequestModel(
            name=self.new_instrument_name,
            owner=self.owner,
            inventoryNumber=new_inventory_number
        )

        response = self._instruments_service.update(
            instrument_id, new_instrument)
        self.assertEqual(response["name"], self.new_instrument_name)
        self.assertEqual(response["owner"], self.owner)
        self.assertEqual(response["inventoryNumber"], new_inventory_number)

        instrument_id = response["instrumentId"]
        response = self._instruments_service.delete(instrument_id)
        self.assertEqual(response, True)

    def test_update_create_update_existing_content_and_delete(self):
        # create a new instrument and update with a existing name and inventory number should return false

        existing_name = f"{self.new_instrument_name} - existing"
        existing_inventory_number = f"{self.inventory_number} - existing"
        existing_instrument = InstrumentsRequestModel(
            name=existing_name,
            owner=self.owner,
            inventoryNumber=existing_inventory_number
        )
        response = self._instruments_service.insert(existing_instrument)

        self.assertEqual(len(response), 6)
        self.assertEqual(response["name"], existing_name)
        self.assertEqual(response["owner"], self.owner)
        self.assertEqual(response["inventoryNumber"],
                         existing_inventory_number)
        existing_instrument_id = response["instrumentId"]

        new_name = f"{self.new_instrument_name} - new"
        new_inventory_number = f"{self.inventory_number} - new"
        new_instrument = InstrumentsRequestModel(
            name=new_name,
            owner=self.owner,
            inventoryNumber=new_inventory_number
        )
        response = self._instruments_service.insert(new_instrument)

        self.assertEqual(len(response), 6)
        self.assertEqual(response["name"], new_name)
        self.assertEqual(response["owner"], self.owner)
        self.assertEqual(response["inventoryNumber"], new_inventory_number)

        new_instrument_id = response["instrumentId"]

        #  update the new instrument entity with existing name and inventory number
        updated_instrument_name = existing_name
        updated_inventory_number = existing_inventory_number
        updated_instrument = InstrumentsRequestModel(
            name=updated_instrument_name,
            owner=self.owner,
            inventoryNumber=updated_inventory_number
        )

        try:
            self._instruments_service.update(
                new_instrument_id, updated_instrument)
        except ValueError as exception:
            self.assertIn("Validation error", str(exception))
        finally:
            response = self._instruments_service.delete(existing_instrument_id)
            self.assertEqual(response, True)
            response = self._instruments_service.delete(new_instrument_id)
            self.assertEqual(response, True)
