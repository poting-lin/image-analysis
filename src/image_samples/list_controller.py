from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from starlette import status
from minio.error import S3Error

from src.util.http_resolvers import BaseResponse
from src.models.samples import SamplesRequestModel, SamplesQueryRequest
from src.data_service.samples_service import SamplesService

router = InferringRouter()


@cbv(router)
class samplesListController():
    """CRUD samples"""

    def __init__(self):
        """Initial shared data"""
        print("init sample list endpoint")
        self.tid = "f112abc4-d49a-4bc9-a058-ddbe2c0bd2ab"
        self.uid = "d700bcda-90c9-436e-932b-75174b65f399"
        self._samples_service = SamplesService(self.tid, self.uid)

    @router.get("/api/samples")
    def get_samples(self):
        """get samples"""

        message = "Succeed."
        try:
            samples_list = self._samples_service.find()
        except S3Error as exc:
            message = f"error occurred: {exc}"
            return (
                message,
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return BaseResponse.succeed(data=samples_list)

    @router.post("/api/samples")
    def create_sample(self, item: SamplesRequestModel):
        """Create sample"""
        print("Create an sample")
        result = {}
        try:
            result = self._samples_service.insert(item)
        except Exception as exception:
            print(f"Creating sample failed: {exception}")
            return BaseResponse.error(message=exception)
        return BaseResponse.succeed(status_code=status.HTTP_202_ACCEPTED, data=result)

    @router.post("/api/samples/query")
    def query_instrument(self, item: SamplesQueryRequest):
        """Query an samples"""
        print("Query an samples")
        result = False
        try:
            result = self._samples_service.if_existed(item)
        except Exception as exception:
            print(f"Query samples failed: {exception}")
            return BaseResponse.error(message=exception)
        return BaseResponse.succeed(status_code=status.HTTP_200_OK, data=result)
