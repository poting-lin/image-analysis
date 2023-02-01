import pymongo
from src.config import ENVIRONMENT_VARIABLES


class MongoDBService:
    def __init__(self):
        self.client = pymongo.MongoClient(
            ENVIRONMENT_VARIABLES["MONGO_ENDPOINT"],
            uuidRepresentation="standard")
        database = f"db{ENVIRONMENT_VARIABLES['ENV']}"
        self.mongo_db = self.client[database]

    def check_if_collection_exists(self, collection_name: str):
        collist = self.mongo_db.list_collection_names()
        if collection_name in collist:
            print(f"The collection: {collection_name} exists.")
        else:
            print(f"The collection: {collection_name} does not exists.")

    def check_if_document_exists(self, collection_name: str, document_json: str):
        collection = self.mongo_db[collection_name]
        document = collection.find_one(document_json)
        print(document)

    def insert_a_document(self, collection_name: str, document_json: str) -> dict:
        collection = self.mongo_db[collection_name]
        object_id = collection.insert_one(document_json).inserted_id
        if len(str(object_id)) == 24:
            return document_json
        else:
            message = f"Delete a instrument failed. instrument content: {document_json}"
            raise Exception(message)

    def find_documents(self, collection_name: str, query_document: dict) -> list:
        collection = self.mongo_db[collection_name]
        counts = collection.find(query_document)
        documents = collection.find(query_document)

        document_list = []
        if len(list(counts)) == 0:
            return document_list

        for document in documents:
            document_list.append(document)
        return document_list

    def delete_one(self, collection_name: str, query_document: dict) -> dict:
        collection = self.mongo_db[collection_name]
        result = collection.delete_one(query_document).raw_result
        if result["n"] == 1 and result["ok"] == 1:
            return True
        else:
            message = f"Delete a instrument failed, total found items: {result['n']}, delete succeed: {result['ok']}."
            raise Exception(message)

    def update_one(self, collection_name: str, query_document: dict, update_content: dict) -> dict:
        collection = self.mongo_db[collection_name]
        new_value = {"$set": update_content}
        try:
            result = collection.update_one(
                query_document, new_value, upsert=True).raw_result

            if result["n"] == 1 and result["ok"] == 1:
                print(
                    f"Update a document succeed, total found items: {result['n']}, delete succeed: {result['ok']}.")
                return update_content
            else:
                message = f"Update a instrument failed, total found items: {result['n']}, delete succeed: {result['ok']}."
                raise Exception(message)
        except Exception as exp:
            print(exp)
