from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from starlette import status
from minio.error import S3Error

from src.util.http_resolvers import BaseResponse
from src.models.instruments import InstrumentsRequestModel, InstrumentsQueryRequest
from src.data_service.instruments_service import InstrumentsService

router = InferringRouter()


@cbv(router)
class InstrumentsListController():
    """CRUD instruments"""

    def __init__(self):
        """Initial shared data"""
        print("init instrument list endpoint")
        self.tid = "f112abc4-d49a-4bc9-a058-ddbe2c0bd2ab"
        self.uid = "d700bcda-90c9-436e-932b-75174b65f399"
        self._instruments_service = InstrumentsService(self.tid, self.uid)

    @router.get("/api/instruments")
    def get_instruments(self):
        """get instruments"""

        message = "Succeed."
        try:
            instruments_list = self._instruments_service.find()
        except S3Error as exc:
            message = f"error occurred: {exc}"
            return (
                message,
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return BaseResponse.succeed(data=instruments_list)

    @router.post("/api/instruments")
    def create_instrument(self, item: InstrumentsRequestModel):
        """Create instrument"""
        print("Create an instrument")
        result = {}
        try:
            print(f"item={item}")
            result = self._instruments_service.insert(item)
        except Exception as exception:
            print(f"Creating instrument failed: {exception}")
            return BaseResponse.error(message=exception)
        return BaseResponse.succeed(status_code=status.HTTP_202_ACCEPTED, data=result)

    @router.post("/api/instruments/query")
    def query_instrument(self, item: InstrumentsQueryRequest):
        """Query an instrument"""
        print("Query an instrument")
        result = False
        try:
            result = self._instruments_service.if_existed(item)
        except Exception as exception:
            print(f"Query instrument failed: {exception}")
            return BaseResponse.error(message=exception)
        return BaseResponse.succeed(status_code=status.HTTP_200_OK, data=result)
