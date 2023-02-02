from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from http import HTTPStatus
from minio.error import S3Error
from uuid import UUID

from src.util.http_resolvers import BaseResponse
from src.data_service.experiments_service import ExperimentsService
from src.models.experiments import ExperimentsRequestModel

router = InferringRouter()


@cbv(router)
class ExperimentsController():
    """Upload files"""

    def __init__(self):
        """Initial shared data"""
        print("init experiments endpoint")
        self.tid = "f112abc4-d49a-4bc9-a058-ddbe2c0bd2ab"
        self.uid = "d700bcda-90c9-436e-932b-75174b65f399"
        self._experiments_service = ExperimentsService(self.tid, self.uid)

    @router.get("/api/experiments/{experiment_id}")
    def get_experiment(self, experiment_id: UUID):
        """get an experiment"""

        message = "Succeed."
        try:
            experiment = self._experiments_service.find_by_experiment_id(
                experiment_id)
        except S3Error as exc:
            message = f"Getting experiment by id failed: {exc}"
            return (
                message,
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )
        except Exception as exc:
            message = f"Getting experiment by id failed: {exc}"
            print(message)
            return BaseResponse.error(message=message)
        return BaseResponse.succeed(data=experiment)

    @router.put("/api/experiments/{experiment_id}")
    def update_experiment(self, experiment_id: UUID, item: ExperimentsRequestModel):
        """update an experiment"""

        message = "Succeed."
        try:
            file_list = self._experiments_service.update(
                experiment_id, item)
        except S3Error as exc:
            message = f"Update experiment by id failed: {exc}"
            return (
                message,
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )
        except Exception as exc:
            message = f"Update experiment by id failed: {exc}"
            print(message)
            return BaseResponse.error(message=message)
        return BaseResponse.succeed(data=file_list)

    @router.delete("/api/experiments/{experiment_id}")
    def delete_experiment(self, experiment_id: str):
        """delete an experiment"""

        message = "Accepted."
        try:
            self._experiments_service.delete(
                experiment_id)
        except S3Error as exc:
            message = f"Delete experiment by id failed: {exc}"
            return (
                message,
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )
        except Exception as exc:
            message = f"Delete experiment by id failed: {exc}, ignore for security reason"
            print(message)
            pass
        return BaseResponse.succeed(status_code=HTTPStatus.ACCEPTED)
