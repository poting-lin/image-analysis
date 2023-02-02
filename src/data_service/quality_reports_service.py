
import os
from typing import Union
from minio import Minio
import pandas as pd
import tempfile
from PIL import Image
import glob
from itertools import groupby
from fastapi import HTTPException
import pandas as pd
from src.data_repository.quality_reports_repository import QualityReportsRepository
from src.config import ENVIRONMENT_VARIABLES


class QualityReportsService():
    def __init__(self, tid: str):
        """Initial shared data"""
        self.client = Minio(ENVIRONMENT_VARIABLES["MINIO_URL"],
                            access_key=ENVIRONMENT_VARIABLES["MINIO_ACCESS_KEY"],
                            secret_key=ENVIRONMENT_VARIABLES["MINIO_SECRET_KEY"],
                            secure=True)
        self.tid = tid
        self._quality_reports_repository = QualityReportsRepository(tid)
        self.experience_jpg_bucket_name = "stage"
        self.analysis_bucket_name = ENVIRONMENT_VARIABLES["BUCKET_RES"]
        self.temp_folder = tempfile.gettempdir()
        self.csv_file_path = self.get_csv_file_path()

    def list_folders(self, analysis_id: str = None):
        folder_name = None if analysis_id is None else f"{analysis_id}"

        try:
            objects = self.client.list_objects(
                "res", prefix=folder_name, recursive=True)
        except Exception as exception:
            return f"get list failed: {exception}"

        folder_list = []
        for obj in objects:
            file_path_name = obj.object_name
            analysis_id = file_path_name.split("/")[0]
            folder_list.append(analysis_id)
        return folder_list

    def get_quality_reports_list(self, analysis_id: Union[str, None] = None):
        quality_reports_list = []

        folder_list = self.list_folders(analysis_id)
        if len(folder_list) != 0:
            for folder in folder_list:
                my_dict = {
                    "analysisId": folder,
                    "datasetId": folder.split("_")[0],
                    "modelId": folder.split("_")[1]
                }
                quality_reports_list.append(my_dict)
        else:
            print(f"No analysis found: analysisId: {analysis_id}")
        return quality_reports_list

    def get_csv_file_path(self, analysis_id: str = None) -> str:
        folder_name = None if analysis_id is None else f"{analysis_id}"

        try:
            objects = self.client.list_objects(
                "res", prefix=folder_name, recursive=True)
        except Exception as exception:
            return f"get list failed: {exception}"

        csv_file_path = None
        for obj in objects:
            file_path_name = obj.object_name
            file_name = file_path_name.split("/")[1]
            file_extension_name = file_name.split(".")[1]
            if file_extension_name == "csv":
                csv_file_path = file_path_name
        return csv_file_path

    def get_dataset_via_file_path(self, csv_file_path: str) -> pd.DataFrame:
        local_document_path = f"{self.temp_folder}/{csv_file_path}"
        self._quality_reports_repository.download_object_from_bucket(
            self.analysis_bucket_name,
            csv_file_path,
            local_document_path
        )
        df = pd.read_csv(local_document_path)
        df = df.reset_index()
        return df

    def get_perdictions_by_analysis_id(self, analysis_id: str) -> dict:
        csv_file_path = self.get_csv_file_path(analysis_id)
        df = self.get_dataset_via_file_path(csv_file_path)
        df = df[["Name", "Materials", "Prediction_Result"]]
        df = df.rename(columns={
            "Name": "name",
            "Materials": "materials",
            "Prediction_Result": "predictionResult"})
        return df.to_dict(orient="records")

    def merge_images(self, files: list, analysis_id: str):
        """Merge two images into one, displayed side by side
        :param file1: path to first image file
        :param file2: path to second image file
        :return: the merged Image object
        """
        groupped_rows = self.get_rows_by_files(files)

        all_images_height = []
        all_images_width = []
        for file in files:
            image = Image.open(file)
            resize_size = 256, 256
            image.thumbnail(resize_size, Image.ANTIALIAS)
            (width, height) = image.size
            all_images_width.append(width)
            all_images_height.append(height)

        img_total_height = 0
        fixed_height = 256
        img_total_width = 0
        fixed_width = 256

        for index_rows, rows in enumerate(groupped_rows, start=1):
            if index_rows == 1:
                for file in rows:
                    img_total_width = img_total_width + fixed_width
            img_total_height = img_total_height + fixed_height
        print(
            f"img_total_height={img_total_height}, img_total_width={img_total_width}")

        result = Image.new('RGB', (img_total_width, img_total_height))
        # start from first row
        current_height = 0
        fixed_height = 256

        prediction_df = self.read_prediction_df(analysis_id)
        for index_rows, rows in enumerate(groupped_rows, start=1):
            if index_rows == 1:
                current_width = 0
                for i, (file, index) in enumerate(zip(rows, range(len(rows)))):
                    image = Image.open(file).convert("RGBA")
                    resize_size = 256, 256
                    image.thumbnail(resize_size, Image.ANTIALIAS)
                    # determine if add red layer
                    if self.determine_add_red_layer(prediction_df, file):
                        print(f"add red layer to the file: {file}")
                        image = self.add_red_layer(image)
                    if i == 0:
                        result.paste(im=image, box=(0, 0))
                    else:
                        result.paste(im=image, box=(current_width, 0))
                    current_width = current_width + fixed_width
            else:
                current_width = 0
                for i, (file, index) in enumerate(zip(rows, range(len(rows)))):
                    image = Image.open(file).convert("RGBA")
                    resize_size = 256, 256
                    image.thumbnail(resize_size, Image.ANTIALIAS)
                    # determine if add red layer
                    if self.determine_add_red_layer(prediction_df, file):
                        print(f"add red layer to the file: {file}")
                        image = self.add_red_layer(image)
                    if i == 0:
                        result.paste(im=image, box=(0, 0))
                    else:
                        result.paste(im=image, box=(
                            current_width, current_height))
                    current_width = current_width + fixed_width
            current_height = current_height + fixed_height

        return result, img_total_width, img_total_height

    def resize_and_upload_to_res(self, img,
                                 img_total_width: int,
                                 img_total_height: int,
                                 ratio: float,
                                 save_location: str,
                                 analysis_id: str):
        print("resize_and_upload_to_res")
        new_width = img_total_width / ratio
        new_height = img_total_height / ratio
        max_allow_width = 15360

        if new_width <= max_allow_width:
            resize_width = max_allow_width
            resize_height = new_height * max_allow_width / new_width
        else:
            resize_width = new_width
            resize_height = new_height

        resize_size = resize_width, resize_height
        img.thumbnail(resize_size, Image.ANTIALIAS)
        img.save(save_location, "JPEG")
        self._quality_reports_repository.upload_object_to_bucket(
            ENVIRONMENT_VARIABLES["BUCKET_RES"],
            f"{analysis_id}/{analysis_id}_analyzed.jpg",
            save_location,
            "image/jpeg")
        print(
            f"Uploading image to minio from local file: {save_location}: analysis_id: {analysis_id} succeed")
        os.remove(save_location)
        print("Removing local temp file succeed.")

    def download_an_object(self, bucket_name, object_name, file_name):
        # Download data of an object.
        self.client.fget_object(bucket_name, object_name, file_name)

    def download_all_objects(self, bucket_name: str, experience_folder: str, is_prediction_file: bool = False) -> Union[None, str]:
        objects = self.client.list_objects(
            bucket_name, prefix=experience_folder, recursive=True)
        for obj in objects:
            # object_name = {experience_id}/jpg_files/{file_name}
            local_path_path = f"{self.temp_folder}/{obj.object_name}"
            print(
                f"start to download an object: {obj.object_name}, in local path: {local_path_path}")
            self.download_an_object(
                bucket_name, obj.object_name, local_path_path)

        if is_prediction_file:
            return local_path_path

    def download_jpg_files(self, analysis_id: str) -> list:
        # download all jpg files to local from res bucket
        dataset_id = analysis_id.split("_")[1]
        local_jpg_path = f"{self.temp_folder}/{dataset_id}/jpg_files"

        self.download_all_objects(
            self.experience_jpg_bucket_name, dataset_id)
        file_list = glob.glob(f"{local_jpg_path}/Tile*.jpg")
        return file_list

    def get_rows_by_files(self, files: list) -> list:
        files.sort()
        groupped_rows = [list(i) for j, i in groupby(files,
                                                     lambda a: a.rsplit('_', 1)[0])]
        return groupped_rows

    def add_red_layer(self, img):
        # check if prediction and material both are the same
        red_img = Image.new('RGBA', (1024, 1024), (255, 0, 0, 100))
        back_im = img.copy()
        back_im.paste(red_img, (0, 0), red_img)
        return back_im

    def determine_add_red_layer(self, df: pd.DataFrame, file_name: str) -> bool:
        image_full_name = file_name.split("/")[-1]
        image_name = image_full_name.split(".")[0]

        file_df = df.loc[df["Name"] == f"{image_name}.tiff"]
        if not file_df.empty:
            file_df = file_df.reset_index()
            if file_df["Materials"][0] != file_df["Prediction_Result"][0]:
                return True
            else:
                return False
        return False

    def read_prediction_df(self, analysis_id: str) -> pd.DataFrame:
        # download prediction result
        csv_file_name = self.get_csv_file_name(analysis_id)
        prediction_result_file_folder = f"{analysis_id}/{csv_file_name}"

        local_path_path = self.download_all_objects(
            "res", prediction_result_file_folder, is_prediction_file=True)
        print(f"prediction result csv file location: {local_path_path}")

        df = pd.read_csv(local_path_path)
        return df

    def generate_image_with_predictions_results(self, analysis_id: str, local_jpg_path: str = None):
        if local_jpg_path is None:
            file_list = self.download_jpg_files(analysis_id)
        else:
            print(f"local_jpg_path={local_jpg_path}")
            file_list = glob.glob(f"{local_jpg_path}/Tile*.jpg")
        img, img_total_width, img_total_height = self.merge_images(
            file_list, analysis_id)
        result_file_path = f"{self.temp_folder}/{analysis_id}/{analysis_id}_analyzed.jpg"

        # 3.1 is around 42.2MB, 5 is around 17mb, 6 is around 11.6
        try:
            self.resize_and_upload_to_res(
                img, img_total_width, img_total_height, 10, result_file_path, analysis_id)
            print(
                f"Generate prediction result image successfully, location: {result_file_path}")
        except Exception as exception:
            message = f"Generate prediction result image failed, location: {result_file_path}; exception: {exception}"
            print(
                message)
            raise RuntimeError(message) from exception

    def get_image_with_prediction_result_layer(self, analysis_id: str, local_jpg_path: str = None):
        print("get_image_with_prediction_result_layer")
        self.generate_image_with_predictions_results(
            analysis_id, local_jpg_path)

        # copy overview image to result bucket
        experience_id = analysis_id.split("_")[1]
        self.duplicate_overview_image_to_res(experience_id, analysis_id)
        return True

    def duplicate_overview_image_to_res(self, experience_id: str, analysis_id: str):
        print("duplicate_overview_image_to_res")
        print("Duplicating overview.jpg to res bucket")
        self._quality_reports_repository.copy_object(
            ENVIRONMENT_VARIABLES["BUCKET_STAGE"],
            f"{experience_id}/overview.jpg",
            ENVIRONMENT_VARIABLES["BUCKET_RES"],
            f"{analysis_id}/overview.jpg"
        )
        print("Duplicating overview.jpg to res bucket succeed")

    def get_csv_file_name(self, analysis_id) -> str:
        # List all object and get a csv file name
        try:
            objects = self.client.list_objects(
                ENVIRONMENT_VARIABLES["BUCKET_RES"], prefix=f"{analysis_id}/", recursive=True)
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
            raise HTTPException(status_code=400, detail="csv file not found")

        return csv_file_name
