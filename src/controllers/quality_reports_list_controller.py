from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from src.data_service.quality_reports_service import QualityReportsService
from src.util.http_resolvers import BaseResponse, get_tid

router = InferringRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@cbv(router)
class QualityReportsListController():
    def __init__(self):
        """Initial shared data"""
        self.tid = "f112abc4-d49a-4bc9-a058-ddbe2c0bd2ab"
        print("init quality reports")
        self._quality_reports_service = QualityReportsService(self.tid)

    @router.get("/api/qualityreports")
    def get(self, token: str = Depends(oauth2_scheme)):
        """quality reports"""
        print(f"token={token}")
        tid = get_tid(token)
        print(f"tid={tid}")
        quality_reports_list = self._quality_reports_service.get_quality_reports_list(
        )

        return BaseResponse.succeed(data=quality_reports_list)
