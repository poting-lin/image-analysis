from fastapi import Request, UploadFile, APIRouter
from fastapi.responses import JSONResponse
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from http import HTTPStatus
from minio.error import S3Error
from typing import List
from src.data_service.credentials_service import CredentialsService
from src.util.helpers import generate_uuid


router = APIRouter(
    prefix="/api/token",
    tags=["items"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


@router.post("/")
def get_token(userEmail: str, userPassword: str):
    """upload files"""
    print("get token")
    user_email = userEmail
    user_password = userPassword

    credentials = CredentialsService(user_email, user_password)
    token = credentials.generate_client_login_auth_token()

    if token:
        return JSONResponse(
            status_code=HTTPStatus.OK, token=token)
    return JSONResponse(
        status_code=HTTPStatus.BAD_REQUEST, errorMessage="userEmail and userPassword invalid")
