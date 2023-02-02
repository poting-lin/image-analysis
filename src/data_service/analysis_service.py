from typing import Union
import pandas as pd
from minio.error import S3Error
import tempfile
import glob
from fastapi import HTTPException
from http import HTTPStatus
from src.data_service.predictions_service import PredictionsService
from src.data_service.quality_reports_service import QualityReportsService
from src.data_service.messages_service import MessagesService
from src.data_service.service_helper import ServiceHelper
from src.config import ENVIRONMENT_VARIABLES, MESSAGE_STATUSES
from minio import Minio
import cv2
import os
import shutil


class AnalysisService():
    def __init__(self, model_id: str, dataset_id: str, analysis_id: str, message_id: str):
        """Initial shared data"""
        self.tid = "f112abc4-d49a-4bc9-a058-ddbe2c0bd2ab"
        self.uid = "d700bcda-90c9-436e-932b-75174b65f399"
        self.temp_folder = tempfile.gettempdir()
        self.client = Minio(ENVIRONMENT_VARIABLES["MINIO_URL"],
                            access_key=ENVIRONMENT_VARIABLES["MINIO_ACCESS_KEY"],
                            secret_key=ENVIRONMENT_VARIABLES["MINIO_SECRET_KEY"],
                            secure=True)
        self.model_id = model_id
        self.dataset_id = str(dataset_id)
        self.model_bucket_name = "models"
        self.document_bucket_name = ENVIRONMENT_VARIABLES["BUCKET_RAW"]
        self.local_document_output_path = f"{self.temp_folder}/{self.dataset_id}_output.csv"
        self.analysis_id = analysis_id
        self.experience_tiff_bucket_name = ENVIRONMENT_VARIABLES["BUCKET_RAW"]
        self.document_file_name = self.look_up_csv_file_name()
        self.document_file_full_path = f"{self.dataset_id}/{self.document_file_name}"
        self.local_document_path = f"{self.temp_folder}/{self.document_file_name}"
        self.local_jpg_path = f"{self.temp_folder}/{self.dataset_id}/jpg_files"
        self.local_tiff_path = f"{self.temp_folder}/{self.dataset_id}/tiff_files"
        self.check_and_create_folder(self.local_jpg_path)
        self.message_id = message_id
        self.messages_service = MessagesService(self.tid, self.uid, "analyses")

    def parse_dataset(self, df) -> str:
        output = pd.DataFrame()
        for i in range(len(df.index)):
            dictionaryObject = df.to_dict('records')[i]

            item_dict = {}
            for index, value in dictionaryObject.items():
                item_dict[index] = f'{value}'
            del item_dict["index"]

            dataset = {
                "predictValues": [
                    item_dict
                ]
            }

            prediction_result = self.predict_data(
                dataset)
            print(
                f"Index: {i}/{len(df.index)}, Prediction result: {prediction_result}, modelId: {self.model_id}, datasetId: {self.dataset_id}")
            dataset["predictValues"][0]["Prediction_Result"] = prediction_result
            output = pd.concat(
                [output, pd.DataFrame([dataset["predictValues"][0]])], ignore_index=True)
        output.to_csv(self.local_document_output_path)
        try:
            model_file_path = os.getcwd() + "/" + "AutoML_MOJO_Model.zip"
            ServiceHelper.remove_tmp_folder(model_file_path)
        except Exception as exception:
            raise RuntimeError(
                f"Removing model file failed: {exception}") from exception
        print("Removing model file succeed")

        output = output.reset_index()

    def predict_data(self, dataset: dict):
        predictions_service = PredictionsService(
            self.model_id)
        predict_result = predictions_service.predict_with_data(
            dataset)
        pared_result = predict_result["message"]
        result = pared_result.replace("Prediction result: ", "")
        return result

    def run_quality_report(self):
        _quality_reports_service = QualityReportsService(self.tid)
        result = _quality_reports_service.get_image_with_prediction_result_layer(
            self.analysis_id, self.local_jpg_path)

        if result:
            print(
                f"Running quality report succeed, analysisId: {self.analysis_id}")
            ServiceHelper.remove_tmp_folder(self.local_jpg_path)
            ServiceHelper.remove_tmp_folder(self.local_tiff_path)
            return True
        else:
            ServiceHelper.remove_tmp_folder(self.local_jpg_path)
            ServiceHelper.remove_tmp_folder(self.local_tiff_path)
            raise RuntimeError(
                "Running quality report failed, analysisId: {self.analysis_id}")

    def upload_result_file_to_stage(self):
        try:
            result_file_name = self.document_file_name.split(
                ".")[0] + "_Prediction_Result" + "." + self.document_file_name.split(
                ".")[1]
            result = self.client.fput_object(
                ENVIRONMENT_VARIABLES["BUCKET_RES"],
                f"{self.analysis_id}/{result_file_name}",
                self.local_document_output_path,
                "text/csv")
            print(
                "created {0} object; etag: {1}, version-id: {2}".format(
                    result.object_name, result.etag, result.version_id,
                ),)
            print(
                f"Analysis completed, analysisId: {self.analysis_id}, file storage location at RES bucket: {self.analysis_id}/{result_file_name}")
        except Exception as exception:
            raise RuntimeError(exception) from exception

    def look_up_csv_file_name(self) -> str:
        # List all object and get a csv file name
        try:
            objects = self.client.list_objects(
                ENVIRONMENT_VARIABLES["BUCKET_RAW"], prefix=f"{self.dataset_id}/", recursive=True)
        except Exception as exception:
            return f"get list failed: {exception}"

        csv_file_name = None
        for obj in objects:
            file_path_name = obj.object_name
            file_name = file_path_name.split("/")[1]
            file_extension_name = file_name.split(".")[1]
            if file_extension_name == "csv":
                csv_file_name = file_name
                return csv_file_name
        if csv_file_name is None:
            raise HTTPException(status_code=400,
                                detail="csv file not found")
        return csv_file_name

    def get_dataset(self) -> pd.DataFrame:

        try:
            self.client.fget_object(
                self.document_bucket_name,
                self.document_file_full_path,
                self.local_document_path)
        except S3Error as exc:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST, detail=f"error occurred: {exc}")
        df = pd.read_csv(self.local_document_path)
        df = df.reset_index()
        return df

    def look_up_csv_file_in_tiff_folder(self) -> str:
        file_list = glob.glob(f"{self.local_tiff_path}/*.csv")
        for file in file_list:
            file_name = file.split(".")[0].split("/")[-1]
            file_extension_name = file.split(".")[-1]
            if file_extension_name == "csv":
                csv_file_name = f"{file_name}.csv"
                return csv_file_name
        if csv_file_name is None:
            raise HTTPException(
                status_code=400, detail="look up csv file in tiff folder not found")

    def upload_an_object_to_bucket(self,
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

    def upload_jpg_to_stage(self):
        file_list = glob.glob(f"{self.local_jpg_path}/*.*")
        for file in file_list:
            file_name = file.split(".")[0].split("/")[-1]
            file_extension = file.split(".")[-1]
            object_name = f"{self.dataset_id}/{file_name}.{file_extension}"
            file_content_type = None
            if file_extension == "csv":
                file_content_type = "text/csv"
            elif file_extension == "jpg":
                file_content_type = "image/jpeg"

            self.upload_an_object_to_bucket(
                ENVIRONMENT_VARIABLES["BUCKET_STAGE"], object_name, file, file_content_type)

    def duplicate_csv_file(self):
        csv_file_path = self.look_up_csv_file_in_tiff_folder()
        shutil.copyfile(f"{self.local_tiff_path}/{csv_file_path}",
                        f"{self.local_jpg_path}/{csv_file_path}")

    def check_and_create_folder(self, folder_path: str):
        parent_folder = f"{self.temp_folder}/{folder_path.split('/')[-2]}"
        if not os.path.isdir(parent_folder):
            os.mkdir(parent_folder)
            print(f"Directory {parent_folder} created.")

        if not os.path.isdir(folder_path):
            os.mkdir(folder_path)
            print(f"Directory {folder_path} created.")

    def convert_tiff_to_jpg(self):
        tiff_file_list = self.download_tiff()

        for file in tiff_file_list:
            file_extension = file.split(".")[-1]
            file_name = file.split(".")[0].split("/")[-1]
            if file_extension == "tiff":
                read = cv2.imread(file)
                outfile = f"{file_name}.jpg"
                cv2.imwrite(f"{self.local_jpg_path}/{outfile}", read,
                            [int(cv2.IMWRITE_JPEG_QUALITY), 50])
                print(f"Write to jpg: {self.local_jpg_path}/{outfile} succeed")

    def download_tiff(self) -> list:
        self.download_all_objects(
            self.experience_tiff_bucket_name, self.dataset_id)
        file_list = glob.glob(f"{self.local_tiff_path}/*.tiff")
        return file_list

    def download_an_object(self, bucket_name, object_name, file_name):
        # Download data of an object.
        self.client.fget_object(bucket_name, object_name, file_name)

    def download_all_objects(self, bucket_name: str, experience_folder: str, is_prediction_file: bool = False) -> Union[None, str]:

        objects = self.client.list_objects(
            bucket_name, prefix=experience_folder, recursive=True)
        for obj in objects:
            file_name = obj.object_name.split("/")[-1]
            local_path_path = f"{self.local_tiff_path}/{file_name}"

            print(
                f"start to download an object: {obj.object_name}, in local path: {local_path_path}")
            self.download_an_object(
                bucket_name, obj.object_name, local_path_path)

        if is_prediction_file:
            return local_path_path

    def make_analysis(self, df: pd.DataFrame) -> pd.DataFrame:

        try:
            self.messages_service.update_status(
                self.message_id, MESSAGE_STATUSES["RUNNING"])
            self.parse_dataset(df)
            self.upload_result_file_to_stage()
            self.convert_tiff_to_jpg()
            self.duplicate_csv_file()
            self.upload_jpg_to_stage()
            self.run_quality_report()
        except Exception as exception:
            self.messages_service.update_status(
                self.message_id, MESSAGE_STATUSES["FAILED"])
            raise RuntimeError(exception) from exception

        # TODO: it return timeout error due to connection issue of MongoDB
        # Find a way to improve it
        messages_service = MessagesService(self.tid, self.uid, "analyses")
        messages_service.update_status(
            self.message_id, MESSAGE_STATUSES["COMPLETED"])
