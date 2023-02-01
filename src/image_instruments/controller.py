from http import HTTPStatus

from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

from src.models.instruments import InstrumentsRequestModel
from minio.error import S3Error
from src.util.http_resolvers import BaseResponse
from src.data_service.instruments_service import InstrumentsService

router = InferringRouter()


@cbv(router)
class InstrumentsController():
    """CRUD instruments"""

    def __init__(self):
        """Initial shared data"""
        print("init instruments endpoint")
        self.tid = "f112abc4-d49a-4bc9-a058-ddbe2c0bd2ab"
        self.uid = "d700bcda-90c9-436e-932b-75174b65f399"
        self._instruments_service = InstrumentsService(self.tid, self.uid)

    @router.get("/api/instruments/{instrument_id}")
    def get_instrument(self, instrument_id: str):
        """get an instrument"""

        message = "Succeed."
        try:
            instrument = self._instruments_service.find_by_instrument_id(
                instrument_id)
        except S3Error as exc:
            message = f"Get instrument by id failed: {exc}"
            return (
                message,
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )
        except Exception as exc:
            message = f"Get instrument by id failed: {exc}"
            print(message)
            return BaseResponse.error(message=message)
        return BaseResponse.succeed(data=instrument)

    @router.put("/api/instruments/{instrument_id}")
    def update_instrument(self, instrument_id: str, item: InstrumentsRequestModel):
        """update an instrument"""

        message = "Succeed."
        try:
            file_list = self._instruments_service.update(
                instrument_id, item)
        except S3Error as exc:
            message = f"Update instrument by id failed: {exc}"
            return (
                message,
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )
        except Exception as exc:
            message = f"Update instrument by id failed: {exc}"
            print(message)
            return BaseResponse.error(message=message)
        return BaseResponse.succeed(data=file_list)

    @router.delete("/api/instruments/{instrument_id}")
    def delete_instrument(self, instrument_id: str):
        """delete an instrument"""

        message = "Accepted."
        try:
            self._instruments_service.delete(
                instrument_id)
        except S3Error as exc:
            message = f"Delete instrument by id failed: {exc}"
            return (
                message,
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )
        except Exception as exc:
            message = f"Delete instrument by id failed: {exc}, ignore for security reason"
            print(message)
            pass
        return BaseResponse.succeed(status_code=HTTPStatus.ACCEPTED)
