from http import HTTPStatus

from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

from src.models.samples import SamplesRequestModel
from minio.error import S3Error
from src.util.http_resolvers import BaseResponse
from src.data_service.samples_service import SamplesService

router = InferringRouter()


@cbv(router)
class samplesController():
    """CRUD samples"""

    def __init__(self):
        """Initial shared data"""
        print("init samples endpoint")
        self.tid = "f112abc4-d49a-4bc9-a058-ddbe2c0bd2ab"
        self.uid = "d700bcda-90c9-436e-932b-75174b65f399"
        self._samples_service = SamplesService(self.tid, self.uid)

    @router.get("/api/samples/{sample_id}")
    def get_sample(self, sample_id: str):
        """get an sample"""

        message = "Succeed."
        try:
            sample = self._samples_service.find_by_sample_id(
                sample_id)
        except S3Error as exc:
            message = f"Update sample by id failed: {exc}"
            return (
                message,
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )
        except Exception as exc:
            message = f"Update sample by id failed: {exc}"
            print(message)
            return BaseResponse.error(message=message)
        return BaseResponse.succeed(data=sample)

    @router.put("/api/samples/{sample_id}")
    def update_sample(self, sample_id: str, item: SamplesRequestModel):
        """update an sample"""

        message = "Succeed."
        try:
            file_list = self._samples_service.update(
                sample_id, item)
        except S3Error as exc:
            message = f"Update sample by id failed: {exc}"
            return (
                message,
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )
        except Exception as exc:
            message = f"Update sample by id failed: {exc}"
            print(message)
            return BaseResponse.error(message=message)
        return BaseResponse.succeed(data=file_list)

    @router.delete("/api/samples/{sample_id}")
    def delete_sample(self, sample_id: str):
        """delete an sample"""

        message = "Accepted."
        try:
            self._samples_service.delete(
                sample_id)
        except S3Error as exc:
            message = f"Delete sample by id failed: {exc}"
            return (
                message,
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )
        except Exception as exc:
            message = f"Delete sample by id failed: {exc}, ignore for security reason"
            print(message)
            pass
        return BaseResponse.succeed(status_code=HTTPStatus.ACCEPTED)
