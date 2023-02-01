from typing import Union
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

import src.services.logservice as log
from starlette import status
import jwt


class BaseResponse:
    def __init__(self) -> None:
        self.base_response = {
            "status_code": status.HTTP_200_OK,
            "message": "",
            "data": None,
        }

    @staticmethod
    def succeed(message: Union[str, dict] = "request succeed", status_code=status.HTTP_200_OK, data: str = None):
        payload = {
            "statusCode": status_code,
            "message": message,
        }
        if data is not None:
            payload["data"] = data
        if isinstance(data, list):
            payload["totalCount"] = len(data)
        elif isinstance(data, dict):
            payload["totalCount"] = 1
        return JSONResponse(
            status_code=status_code,
            content=jsonable_encoder(payload))

    @staticmethod
    def error(message="request failed", status_code=status.HTTP_400_BAD_REQUEST):
        if isinstance(message, HTTPException):
            exception_message = message.detail
        else:
            exception_message = str(message)
        return JSONResponse(
            status_code=status_code,
            content={
                "statusCode": status_code,
                "message": exception_message,
            })


def get_tid(token_string: str) -> str:
    decoded_string = jwt.decode(token_string, options={
        "verify_signature": False})
    return decoded_string["tid"]
