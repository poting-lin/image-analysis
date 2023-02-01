import uuid
import time
from src.data_repository.messages_repository import MessagesRepository


class MessagesService:
    def __init__(self, tid: str, uid: str, message_type: str = None):
        self.messages_repository = MessagesRepository()
        self.collection: str = "messages"
        self.message_type: str = message_type
        self.tid = tid
        self.uid = uid

    def send_analysis_message(self, message_id: str, message_status: str, analysis_id: str) -> bool:
        message = {
            "messageId": message_id,
            "messageType": self.message_type,
            "messageContent": {
                "tid": self.tid,
                "uid": self.uid,
                "analysisName": None,
                "eventId": str(uuid.uuid4()),
                "analysisId": analysis_id,
                "runtimeStatus": message_status
            },
            "messageCreatedAt": time.time(),
            "messageLastUpdatedAt": None
        }
        return self.messages_repository.insert_a_document(self.collection, message)

    def send_message(self, message_id: str, message_content: dict) -> bool:
        message = {
            "messageId": message_id,
            "messageType": self.message_type,
            "messageContent": message_content
        }
        return self.messages_repository.insert_a_document(self.collection, message)

    def update_status(self, message_id: str, status: str) -> bool:
        return self.messages_repository.update_one(
            "messages",
            {
                "messageId": message_id
            }, {
                "messageContent.runtimeStatus": status,
                "messageLastUpdatedAt": time.time()
            })

    def delete_one_message(self, message_id: str) -> bool:
        return self.messages_repository.delete_one(
            self.collection, {
                "messageId": message_id
            }).raw_result

    def get_messages_not_completed(self) -> list:
        query = {"$and": [
            {"messageType": self.message_type},
            {"messageContent.runtimeStatus": {
                "$ne": "pending"
            }}
        ]}
        return self.messages_repository.find_documents(
            self.collection, query)

    def get_all_messages(self) -> list:
        query = None
        if self.message_type is not None:
            query = {"messageType": self.message_type}
        message_list = self.messages_repository.find_documents(
            self.collection, query)
        message_list_without_object_id = self.remove_object_id(message_list)
        reorder_message_list = self.reorder_by_updated_time(
            message_list_without_object_id)
        return self.convert_timestamp_to_datetime(reorder_message_list)

    def remove_object_id(self, message_list: list) -> list:
        for message in message_list:
            message.pop("_id")
        return message_list

    def reorder_by_updated_time(self, message_list: list) -> list:
        return sorted(message_list, key=lambda k: k["messageCreatedAt"], reverse=True)

    def convert_timestamp_to_datetime(self, message_list: list) -> str:
        converted_message_list = []
        for message in message_list:
            message["messageCreatedAt"] = time.strftime(
                '%Y-%m-%d %H:%M:%S',
                time.localtime(
                    message["messageCreatedAt"]
                ))
            if message["messageLastUpdatedAt"] is not None:
                message["messageLastUpdatedAt"] = time.strftime(
                    '%Y-%m-%d %H:%M:%S',
                    time.localtime(
                        message["messageLastUpdatedAt"]
                    ))
            converted_message_list.append(message)
        return converted_message_list
