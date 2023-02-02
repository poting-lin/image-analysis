from http import HTTPStatus
from minio import Minio
import os.path
import tempfile
import zipfile
import json
from minio.error import S3Error
from fastapi import HTTPException
from subprocess import check_output
from src.config import ENVIRONMENT_VARIABLES
from src.data_service.service_helper import ServiceHelper


class PredictionsService:
    def __init__(self, model_id: str):
        """Initial shared data"""
        self.client = Minio(ENVIRONMENT_VARIABLES["MINIO_URL"],
                            access_key=ENVIRONMENT_VARIABLES["MINIO_ACCESS_KEY"],
                            secret_key=ENVIRONMENT_VARIABLES["MINIO_SECRET_KEY"],
                            secure=True)
        self.temp_folder = tempfile.gettempdir()
        self.model_bucket_name = "models"
        self.model_id = model_id
        self.project_file_name = f"DeployPackage-{self.model_id}.zip"
        self.model_name = "AutoML_MOJO_Model.zip"
        self.local_model_path = self.model_name
        self.local_project_path = f"{self.temp_folder}/{self.project_file_name}"
        self.model_path_in_project = f"src/{self.model_name}"

    def predict_with_data(self, data: dict) -> str:
        # check if model has loaded
        if os.path.exists(self.local_project_path):
            pass
        else:
            try:
                self.client.fget_object(
                    self.model_bucket_name,
                    self.project_file_name,
                    self.local_project_path)
            except S3Error as exc:
                ServiceHelper.remove_tmp_folder(self.local_project_path)
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST, detail=f"error occurred: {exc}") from exc

        try:
            with zipfile.ZipFile(self.local_project_path) as z:
                with open(self.local_model_path, 'wb') as f:
                    f.write(z.read(self.model_path_in_project))
        except KeyError as exception:
            message = f"Access model failed: {exception}, modelId: {self.model_id}"
            print(message)
            ServiceHelper.remove_tmp_folder(self.model_path_in_project)
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=message) from exception

        try:
            result = check_output(
                ["java", "-jar", "predict.jar", json.dumps(data)]).decode("utf-8")
            predict_result = {
                "message": result.strip()}
        except Exception as exception:
            predict_result = {
                "message": "Sorry, we couldn't generate your prediction."}
            ServiceHelper.remove_tmp_folder(self.model_path_in_project)
            raise exception
        return predict_result
