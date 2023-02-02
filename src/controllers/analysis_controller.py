from fastapi import BackgroundTasks
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from starlette import status
import uuid


from src.data_service.analysis_service import AnalysisService
from src.data_service.messages_service import MessagesService
from src.models.analysis import AnalysisRequest
from src.util.http_resolvers import BaseResponse
from src.config import MESSAGE_STATUSES
import src.services.logservice as log

router = InferringRouter()  # Step 1: Create a router


@cbv(router)
class AnalysisController():
    """Analysis dataset"""

    def __init__(self):
        self.tid = "f112abc4-d49a-4bc9-a058-ddbe2c0bd2ab"
        self.uid = "d700bcda-90c9-436e-932b-75174b65f399"
        self.message_id = str(uuid.uuid4())
        self.run_id = str(uuid.uuid4())
        self.messages_service = MessagesService(self.tid, self.uid, "analyses")

    @router.post("/api/analysis")
    def run_analysis(self, item: AnalysisRequest, background_tasks: BackgroundTasks):
        """trigger a etl pipeline"""
        log.info("trigger analysis pipeline ")
        if item.modelId is None:
            error_message = "model Id not provided"
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST, content=error_message)
        analysis_id = f"{item.modelId}_{item.datasetId}"
        self.messages_service.send_analysis_message(
            self.message_id, MESSAGE_STATUSES["PENDING"], analysis_id)
        try:
            analysis_service = AnalysisService(
                item.modelId, item.datasetId, analysis_id, self.message_id)
            total_items_df = analysis_service.get_dataset()
            background_tasks.add_task(
                analysis_service.make_analysis, total_items_df)
            data = {
                "analysisId": analysis_id,
                "runId": self.run_id,
                "modelId": str(item.modelId),
                "datasetId": str(item.datasetId),
                "totalItems": len(total_items_df.index)
            }

            return BaseResponse.succeed(status_code=status.HTTP_202_ACCEPTED, data=data)
        except Exception as exception:
            print(f"Making analysis failed: {exception}")
            if isinstance(exception, HTTPException):
                return BaseResponse.error(message=exception.detail)
            return BaseResponse.error(message=exception)
