from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from starlette import status
from minio.error import S3Error

from src.models.experiments import ExperimentsRequestModel
from src.data_service.experiments_service import ExperimentsService
from src.util.http_resolvers import BaseResponse

router = InferringRouter()


@cbv(router)
class DatasetsListController():
    """Upload files"""

    def __init__(self):
        """Initial shared data"""
        print("init experiments list endpoint")
        self.tid = "f112abc4-d49a-4bc9-a058-ddbe2c0bd2ab"
        self.uid = "d700bcda-90c9-436e-932b-75174b65f399"
        self._experiments_service = ExperimentsService(self.tid, self.uid)

    @router.get("/api/experiments")
    def get_experiments(self):
        """get experiments"""

        message = "Succeed."
        try:
            experiments_list = self._experiments_service.find()
        except S3Error as exc:
            message = f"error occurred: {exc}"
            return (
                message,
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return BaseResponse.succeed(data=experiments_list)

    @router.post("/api/experiments")
    def create_experiment(self, item: ExperimentsRequestModel):
        """upload files"""
        print("create a experiment")

        result = {}
        try:
            result = self._experiments_service.insert(item)
        except Exception as exception:
            print(f"Creating experiment failed: {str(exception)}")
            return BaseResponse.error(message=exception)
        return BaseResponse.succeed(status_code=status.HTTP_200_OK, data=result)
