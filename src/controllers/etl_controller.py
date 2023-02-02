from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from http import HTTPStatus
from src.data_service.etl_service import EtlService
import src.services.logservice as log

router = InferringRouter()  # Step 1: Create a router


@cbv(router)
class EtlController():
    """Upload files"""
    tenant_id = "f112abc4-d49a-4bc9-a058-ddbe2c0bd2ab"

    @router.post("/api/etl/{document_id}")
    def run_etl(self, document_id: str):
        """trigger a etl pipeline"""
        log.info("trigger etl pipeline files")
        if document_id is None:
            error_message = "document Id not provided"
            return JSONResponse(
                status_code=HTTPStatus.BAD_REQUEST, content=error_message)
        etl_service = EtlService()
        df, file_name = etl_service.get_all_objects_in_raw()
        etl_service.raw_to_stage(df, file_name)
        etl_service.stage_to_ai_designer(df, file_name)
        return JSONResponse(
            status_code=HTTPStatus.OK, content=f"The csv files merge and save in stage, copy to AI designer succeed, document Id: {document_id}")
