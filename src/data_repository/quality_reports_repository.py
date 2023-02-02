import os
from src.config import ENVIRONMENT_VARIABLES
from minio import Minio
from minio.error import S3Error
from minio.commonconfig import CopySource
from http import HTTPStatus
from fastapi import HTTPException
import src.services.logservice as log


class QualityReportsRepository():
    def __init__(self, tid: str):
        """Initial shared data"""
        self.client = Minio(ENVIRONMENT_VARIABLES["MINIO_URL"],
                            access_key=ENVIRONMENT_VARIABLES["MINIO_ACCESS_KEY"],
                            secret_key=ENVIRONMENT_VARIABLES["MINIO_SECRET_KEY"],
                            secure=True)
        self.tid = tid
        self.model_bucket_name = "models"
        self.analysis_bucket_name = ENVIRONMENT_VARIABLES["BUCKET_RES"]

    def list_folder(self):
        try:
            objects = self.client.list_objects(
                "res", prefix="", recursive=True)
        except Exception as exception:
            return f"get list failed: {exception}"

        folder_list = []
        for obj in objects:
            file_path_name = obj.object_name
            analysis_id = file_path_name.split("/")[0]
            folder_list.append(analysis_id)
        return folder_list

    def check_bucket(self, bucket_name) -> bool:
        if self.client.bucket_exists(bucket_name):
            log.info(f"{bucket_name} exists")
            return True
        else:
            log.warning(f"{bucket_name} does not exist")
            return False

    def upload_object_to_bucket(self,
                                bucket_name: str,
                                object_name: str,
                                local_file_path: str,
                                content_type: str = "application/octet-stream"
                                ):
        try:
            self.client.fput_object(
                bucket_name, object_name, local_file_path, content_type)
        except Exception as exception:
            raise RuntimeError(exception) from exception
        print(
            f"Upload object: {object_name} to bucket: {bucket_name} from local: {local_file_path}, succeed.")

    def download_object_from_bucket(self, bucket_name: str,  object_name: str, local_file_path: str):
        try:
            self.client.fget_object(
                bucket_name,
                object_name,
                local_file_path)
        except S3Error as exc:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                detail=f"download object error occurred: {exc}") from exc

    def copy_object(self,
                    from_bucket_name: str,
                    from_object_name: str,
                    to_bucket_name: str,
                    to_object_name: str
                    ):
        try:
            self.client.copy_object(
                to_bucket_name,
                to_object_name,
                CopySource(from_bucket_name, from_object_name),)
        except S3Error as exc:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                detail=f"copy object error occurred: {exc}") from exc

    def delete_files_in_temp_folder(self, temp_folder: str):
        for f in os.listdir(temp_folder):
            os.remove(os.path.join(dir, f))
        print(f"Removing files under local temp folder succeed: {temp_folder}")
