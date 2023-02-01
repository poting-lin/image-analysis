import time
from typing import Tuple, Union
import uuid
from src.models.instruments import InstrumentsRequestModel, InstrumentsQueryRequest
from src.services.mongodb import MongoDBService


class InstrumentsService:
    def __init__(self, tid: str, uid: str):
        self.mongodb_service = MongoDBService()
        self.collection: str = "instruments"
        self.tid = tid
        self.uid = uid
        self.exception_message = []

    # pylint: disable=no-self-argument
    def validate_insert(function):
        def wrapper(*args, **kwargs):
            # prepare arguments data
            request_data = args[1]
            self_service = args[0]
            # check if inventoryNumber already exists in database
            inventory_number_list = self_service.find_by_inventory_number(
                request_data.inventoryNumber)
            if len(inventory_number_list) > 0:
                self_service.exception_message.append(
                    "Inventory number already exists.")
            # check if there is a item with the same name and inventoryNumber
            name_inventory_number_list = self_service.find_by_name_and_inventory_number(
                request_data.name, request_data.inventoryNumber)
            if len(name_inventory_number_list) > 0:
                self_service.exception_message.append(
                    "A entity with the same same and inventory number found.")
            # merge above functions with InstrumentsRequestModel
            if len(self_service.exception_message) > 0:
                raise ValueError(
                    f"Validation error: {self_service.exception_message}")
            # pylint: disable=not-callable
            return function(*args, **kwargs)
        return wrapper

    # pylint: disable=no-self-argument
    def validate_update(function):
        def wrapper(*args, **kwargs):
            # prepare arguments data

            self_service = args[0]
            instrument_id = args[1]
            request_data = args[2]
            # check if inventoryNumber already exists in database
            inventory_number_list = self_service.find_by_inventory_number(
                request_data.inventoryNumber)
            result = self_service.find_by_instrument_id(instrument_id)

            # check if new inventoryNumber is the same as the old one
            # check in inventory number the same as the one in the database, if it is, inventory_number_list > 1
            if result["inventoryNumber"] == request_data.inventoryNumber and len(inventory_number_list) > 1:
                self_service.exception_message.append(
                    "Update with a new Inventory number already exists.")
            elif result["inventoryNumber"] != request_data.inventoryNumber and len(inventory_number_list) > 0:
                self_service.exception_message.append(
                    "Update with a new Inventory number already exists.")
            # check if there is a item with the same name and inventoryNumber
            name_inventory_number_list = self_service.find_by_name_and_inventory_number(
                request_data.name, request_data.inventoryNumber)
            if len(name_inventory_number_list) > 1:
                self_service.exception_message.append(
                    "A entity with the same name and inventory number found.")
            # merge above functions with InstrumentsRequestModel
            if len(self_service.exception_message) > 0:
                raise ValueError(
                    f"Validation error: {self_service.exception_message}")
            # pylint: disable=not-callable
            return function(*args, **kwargs)
        return wrapper

    @validate_insert
    def insert(self, content: InstrumentsRequestModel) -> dict:
        document_content = {
            "instrumentId": str(uuid.uuid4()),
            "name": content.name,
            "owner": content.owner,
            "inventoryNumber": content.inventoryNumber,
            "createdAt": time.time(),
            "lastUpdatedAt": None
        }
        result = self.mongodb_service.insert_a_document(
            self.collection, document_content)
        instrument_without_object_id = self.remove_object_id(
            result)

        return self.convert_timestamp_to_datetime(instrument_without_object_id)

    def find_by_name_and_inventory_number(self, name: str, inventory_number: str) -> list:
        query = {
            "name": name,
            "inventoryNumber": inventory_number
        }
        return self.mongodb_service.find_documents(
            self.collection, query)

    def if_existed(self, item: InstrumentsQueryRequest) -> Tuple[bool, str]:
        find_inventory_number = self.find_by_inventory_number(
            item.inventoryNumber)

        # check when creating a new item
        if item.instrumentId is None or item.instrumentId == "" or len(item.instrumentId) == 0:
            if len(find_inventory_number) == 1:
                return True, "Inventory number already exists."

        # check when updating an item
        elif item.instrumentId is not None and len(item.instrumentId) > 0:
            if len(find_inventory_number) == 1 and find_inventory_number[0]["instrumentId"] != item.instrumentId:
                return True, "Inventory number already exists."
        return False, None

    def find_by_inventory_number(self, inventory_number: str) -> bool:
        query = {"inventoryNumber": inventory_number}
        return self.mongodb_service.find_documents(
            self.collection, query)

    def delete(self, instrument_id: str) -> bool:
        return self.mongodb_service.delete_one(
            self.collection, {
                "instrumentId": instrument_id
            })

    @validate_update
    def update(self, instrument_id: str, content: InstrumentsRequestModel) -> bool:
        self.mongodb_service.update_one(
            self.collection,
            {
                "instrumentId": instrument_id
            }, {
                "name": content.name,
                "owner": content.owner,
                "inventoryNumber": content.inventoryNumber,
                "lastUpdatedAt": time.time()
            })
        return self.find_by_instrument_id(instrument_id)

    def find(self, query: str = None) -> list:
        instrument_list = self.mongodb_service.find_documents(
            self.collection, query)
        instrument_list_without_object_id = self.remove_object_id(
            instrument_list)
        reorder_instrument_list = self.reorder_by_updated_time(
            instrument_list_without_object_id)
        return self.convert_timestamp_to_datetime(reorder_instrument_list)

    def find_by_instrument_id(self, instrument_id: str) -> dict:
        query = {"instrumentId": instrument_id}
        instrument_list = self.mongodb_service.find_documents(
            self.collection, query)
        if len(instrument_list) > 1:
            raise Exception("more than one instrument found")
        elif len(instrument_list) == 0:
            raise Exception("no instrument found")
        else:
            instrument_list_without_object_id = self.remove_object_id(
                instrument_list[0])
            return self.convert_timestamp_to_datetime(instrument_list_without_object_id)

    def remove_object_id(self, instruments: Union[list, dict]) -> Union[list, dict]:
        if isinstance(instruments, list):
            for instrument in instruments:
                instrument.pop("_id")
            return instruments
        else:
            del instruments["_id"]
            return instruments

    def reorder_by_updated_time(self, instrument_list: list) -> list:
        return sorted(instrument_list, key=lambda k: k["createdAt"], reverse=True)

    def convert_timestamp_to_datetime(self, instruments: Union[list, dict]) -> Union[list, dict]:
        if isinstance(instruments, list):
            converted_instrument_list = []
            for instrument in instruments:
                instrument["createdAt"] = time.strftime(
                    '%Y-%m-%d %H:%M:%S',
                    time.localtime(
                        instrument["createdAt"]
                    ))
                if instrument["lastUpdatedAt"] is not None:
                    instrument["lastUpdatedAt"] = time.strftime(
                        '%Y-%m-%d %H:%M:%S',
                        time.localtime(
                            instrument["lastUpdatedAt"]
                        ))
                converted_instrument_list.append(instrument)
            return converted_instrument_list
        else:
            instruments["createdAt"] = time.strftime(
                '%Y-%m-%d %H:%M:%S',
                time.localtime(
                    instruments["createdAt"]
                ))
            if instruments["lastUpdatedAt"] is not None:
                instruments["lastUpdatedAt"] = time.strftime(
                    '%Y-%m-%d %H:%M:%S',
                    time.localtime(
                        instruments["lastUpdatedAt"]
                    ))
            return instruments
