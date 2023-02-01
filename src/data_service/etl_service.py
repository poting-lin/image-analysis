from src.config import ENVIRONMENT_VARIABLES
from minio import Minio
from src.data_repository.etl_repository import EtlRepository


class EtlService():
    def __init__(self):
        """Initial shared data"""
        self.etl_repository = EtlRepository(
            ENVIRONMENT_VARIABLES["MINIO_ENDPOINT"], ENVIRONMENT_VARIABLES["MINIO_ACCESS_KEY"], ENVIRONMENT_VARIABLES["MINIO_SECRET_KEY"])

    def get_all_objects_in_raw(self):
        return self.etl_repository.get_all_objects("raw")

    def raw_to_stage(self, df, file_name):
        """Merge csv files in raw and upload to stage"""
        self.etl_repository.upload_object("stage", file_name, df)

    def stage_to_ai_designer(self, df, file_name):
        """Copy csv file in stage and upload to AI designer"""
        self.etl_repository.upload_object(
            "designerbucket", file_name, df)
