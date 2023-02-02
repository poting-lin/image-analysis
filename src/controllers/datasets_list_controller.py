from fastapi import Header, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from http import HTTPStatus
from typing import List
from minio.error import S3Error

from src.data_service.files_service import FileService
from src.util.http_resolvers import BaseResponse

router = InferringRouter()


@cbv(router)
class DatasetsListController():
    """Upload files"""

    def __init__(self):
        """Initial shared data"""
        print("init datasets list endpoint")
        self.tenant_id = "f112abc4-d49a-4bc9-a058-ddbe2c0bd2ab"

    @router.get("/api/datasets")
    def get_files(self):
        """get filter options"""

        message = "Succeed."
        try:
            fileservice = FileService()
            file_list = fileservice.get_filelist_datasets()
        except S3Error as exc:
            message = f"error occurred: {exc}"
            return (
                message,
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )
        return BaseResponse.succeed(data=file_list)

    @router.post("/api/datasets")
    async def upload_files(self, fileField: List[UploadFile], datasetId: str = Form()):
        """upload files"""
        print("upload dataset")
        files = fileField

        file = FileService()
        file_validated = file.validate_file_extension(files)

        # TODO: upload validated files to minio
        if file_validated["all_validated"]:
            file_list = file.upload_files(files, datasetId)
            data = {
                "datasetId": datasetId,
                "fileList": file_list
            }
            return BaseResponse.succeed(data=data)
        return JSONResponse(
            status_code=HTTPStatus.BAD_REQUEST, content=file_validated)
