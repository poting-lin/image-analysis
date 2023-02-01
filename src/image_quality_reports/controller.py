import io
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import StreamingResponse
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from src.data_service.quality_reports_service import QualityReportsService
from src.util.http_resolvers import BaseResponse

router = InferringRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@cbv(router)
class QualityReportsController():
    def __init__(self):
        """Initial shared data"""
        self.tid = "f112abc4-d49a-4bc9-a058-ddbe2c0bd2ab"
        print("init quality reports")
        self._quality_reports_service = QualityReportsService(self.tid)

    @router.get("/api/qualityreports/{analysis_id}/images")
    def get_image(self, analysis_id: str, token: str = Depends(oauth2_scheme)):
        """quality reports"""
        # result = self._quality_reports_service.get_image_with_prediction_result_layer(
        #     analysis_id)
        # if result:
        image = f"http://MINIO_URL/res/{analysis_id}/{analysis_id}_analyzed.jpg"
        return BaseResponse.succeed(data=image)

        # response = StreamingResponse(io.BytesIO(
        #     image.tobytes()), media_type="image/jpeg")
        # response.headers[
        #     "Content-Disposition"] = f"attachment; filename={analysis_id}_analyzed.jpg"
        # return response

    # @router.get("/api/qualityreports/{analysis_id}")
    # def get(self, analysis_id: str, token: str = Depends(oauth2_scheme)):
    #     """quality reports"""
    #     quality_reports_list = self._quality_reports_service.get_perdictions_by_analysis_id(
    #         analysis_id)
    #     return BaseResponse.succeed(data=quality_reports_list)
