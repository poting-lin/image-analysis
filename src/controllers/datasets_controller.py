from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from http import HTTPStatus
from minio.error import S3Error

from src.data_service.files_service import FileService
from src.util.http_resolvers import BaseResponse

router = InferringRouter()


@cbv(router)
class DatasetsController():
    """Upload files"""

    def __init__(self):
        """Initial shared data"""
        print("init datasets endpoint")
        self.tenant_id = "f112abc4-d49a-4bc9-a058-ddbe2c0bd2ab"

    @router.get("/api/datasets/{dataset_id}")
    def get_files(self, dataset_id: str):
        """get filter options"""

        message = "Succeed."
        try:
            fileservice = FileService()
            file_list = fileservice.get_filelist_datasets(dataset_id)
        except S3Error as exc:
            message = f"error occurred: {exc}"
            return (
                message,
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )
        return BaseResponse.succeed(data=file_list)
