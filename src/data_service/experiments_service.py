import time
from typing import Tuple, Union
from uuid import UUID, uuid4
from src.models.experiments import ExperimentsRequestModel, ExperimentsResponseModel
from src.services.mongodb import MongoDBService


class ExperimentsService:
    def __init__(self, tid: str, uid: str):
        self.mongodb_service = MongoDBService()
        self.collection: str = "experiments"
        self.tid = tid
        self.uid = uid
        self.exception_message = []

    # pylint: disable=no-self-argument
    def validate_insert(function):
        def wrapper(*args, **kwargs):
            # prepare arguments data
            request_data = args[1]
            self_service = args[0]
            # check if datasetId already exists in database
            dataset_id_list = self_service.find_by_dataset_id(
                request_data.datasetId)
            if len(dataset_id_list) > 0:
                self_service.exception_message.append(
                    "datasetId already exists.")
            # check if there is a item with the same conditions
            duplicate_entities_list = self_service.find_duplicate_entities(
                request_data)
            if len(duplicate_entities_list) > 0:
                self_service.exception_message.append(
                    "A entity with the same content found.")
            # merge above functions with SamplesRequestModel
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
            experiment_id = args[1]
            request_data = args[2]
            # check if datasetId already exists in database
            dataset_id_list = self_service.find_by_dataset_id(
                request_data.datasetId)
            result = self_service.find_by_experiment_id(experiment_id)
            # check if new DatasetId is the same as the old one
            # check in DatasetId the same as the one in the database, if it is, dataset_id_list > 1

            if result["datasetId"] == request_data.datasetId and len(dataset_id_list) > 1:
                self_service.exception_message.append(
                    "Update with a new DatasetId already exists.")
            elif result["datasetId"] != request_data.datasetId and len(dataset_id_list) > 0:
                self_service.exception_message.append(
                    "Update with a new DatasetId already exists.")
            # check if there is a item with the same name and inventoryNumber
            duplicate_entities_list = self_service.find_duplicate_entities(
                request_data)
            if len(duplicate_entities_list) > 1:
                self_service.exception_message.append(
                    "A entity with the same content found.")
            # merge above functions with SamplesRequestModel
            if len(self_service.exception_message) > 0:
                raise ValueError(
                    f"Validation error: {self_service.exception_message}")
            # pylint: disable=not-callable
            return function(*args, **kwargs)
        return wrapper

    @validate_insert
    def insert(self, content: ExperimentsRequestModel) -> dict:
        document_content = {
            "experimentId": uuid4(),
            "sampleId": content.sampleId,
            "instrumentId": content.instrumentId,
            "datasetId": content.datasetId,
            "experimentTitle": content.experimentTitle,
            "researcherName": content.researcherName,
            "laboratoryName": content.laboratoryName,
            "startAt": content.startAt,
            "endAt": content.endAt,
            "lastUpdatedAt": None
        }
        result = self.mongodb_service.insert_a_document(
            self.collection, document_content)
        experiment_without_object_id = self.remove_object_id(
            result)

        return ExperimentsResponseModel(**experiment_without_object_id)

    def find_by_name_and_inventory_number(self, name: str, inventory_number: str) -> list:
        query = {
            "name": name,
            "inventoryNumber": inventory_number
        }
        return self.mongodb_service.find_documents(
            self.collection, query)

    def if_dataset_id_in_existed(self, item: ExperimentsRequestModel) -> Tuple[bool, str]:
        find_dataset_id = self.find_by_dataset_id(
            item.datasetId)

        # check when creating a new item
        if item.datasetId is None or item.datasetId == "" or len(item.datasetId) == 0:
            if len(find_dataset_id) == 1:
                return True, "datasetId already exists."

        # check when updating an item
        elif item.datasetId is not None and len(item.datasetId) > 0:
            if len(find_dataset_id) == 1 and find_dataset_id[0]["datasetId"] != item.datasetId:
                return True, "datasetId already exists."
        return False, None

    def find_by_dataset_id(self, dataset_id: str) -> bool:
        query = {"datasetId": dataset_id}
        return self.mongodb_service.find_documents(
            self.collection, query)

    def find_duplicate_entities(self, request_data: ExperimentsRequestModel) -> bool:
        query = {
            "sampleId": request_data.sampleId,
            "instrumentId": request_data.instrumentId,
            "datasetId": request_data.datasetId,
            "experimentTitle": request_data.experimentTitle,
            "researcherName": request_data.researcherName,
            "laboratoryName": request_data.laboratoryName,
            "startAt": request_data.startAt,
            "endAt": request_data.endAt,
        }
        return self.mongodb_service.find_documents(
            self.collection, query)

    def delete(self, sample_id: str) -> bool:
        return self.mongodb_service.delete_one(
            self.collection, {
                "sampleId": sample_id
            })

    @validate_update
    def update(self, experiment_id: UUID, content: ExperimentsRequestModel):
        self.mongodb_service.update_one(
            self.collection,
            {
                "experimentId": experiment_id
            }, {
                "sampleId": content.sampleId,
                "instrumentId": content.instrumentId,
                "datasetId": content.datasetId,
                "experimentTitle": content.experimentTitle,
                "researcherName": content.researcherName,
                "laboratoryName": content.laboratoryName,
                "startAt": content.startAt,
                "endAt": content.endAt,
                "lastUpdatedAt": time.time()
            })
        experiment_updated = self.find_by_experiment_id(experiment_id)
        return ExperimentsResponseModel(**experiment_updated)

    def find(self, query: str = None) -> list:
        experiment_list = self.mongodb_service.find_documents(
            self.collection, query)

        response_list = []
        for experiment in experiment_list:
            response_list.append(ExperimentsResponseModel(**experiment))

        return response_list

    def find_by_experiment_id(self, experiment_id: UUID) -> dict:
        query = {"experimentId": experiment_id}
        experiment_list = self.mongodb_service.find_documents(
            self.collection, query)
        if len(experiment_list) > 1:
            raise Exception("more than one experiment found")
        elif len(experiment_list) == 0:
            raise Exception("no experiment found")

        experiment_list_without_object_id = self.remove_object_id(
            experiment_list[0])

        return experiment_list_without_object_id

    def remove_object_id(self, experiments: Union[list, dict]) -> Union[list, dict]:
        if isinstance(experiments, list):
            for experiment in experiments:
                experiment.pop("_id")
            return experiments
        else:
            del experiments["_id"]
            return experiments

    def reorder_by_updated_time(self, sample_list: list) -> list:
        return sorted(sample_list, key=lambda k: k["startAt"], reverse=True)

    def convert_timestamp_to_datetime(self, experiments: Union[list, dict]) -> Union[list, dict]:
        if isinstance(experiments, list):
            converted_sample_list = []
            for experiment in experiments:
                if experiment["lastUpdatedAt"] is not None:
                    experiment["lastUpdatedAt"] = time.strftime(
                        '%Y-%m-%d %H:%M:%S',
                        time.localtime(
                            experiment["lastUpdatedAt"]
                        ))
                converted_sample_list.append(experiment)
            return converted_sample_list
        else:
            if experiments["lastUpdatedAt"] is not None:
                experiments["lastUpdatedAt"] = time.strftime(
                    '%Y-%m-%d %H:%M:%S',
                    time.localtime(
                        experiments["lastUpdatedAt"]
                    ))
            return experiments
