from http import HTTPStatus
import jwt
from fastapi import HTTPException
from minio import Minio
from src.data_repository.files_repository import FileRepository
import src.services.logservice as log
from src.config import ENVIRONMENT_VARIABLES


class CredentialsService():
    def __init__(self, user_email: str, user_password: str):
        """Initial shared data"""
        self.user_email = None
        self.user_password = None

    def generate_client_login_auth_token(self):
        """Returns the token value to use in Authorization headers.
        Reads the token from the server's response to a Client Login request and
        creates header value to use in requests.

        Args:
        http_body: str The body of the server's HTTP response to a Client Login
            request

        Returns:
        The value half of an Authorization header.
        """
        # List all object paths in bucket that begin with my-prefixname.
        user_info = {
            "iss": "Online JWT Builder",
            "iat": 1628257164,
            "exp": 1659793164,
            "aud": "www.example.com",
            "sub": "test@test.com",
            "tid": "9a3ea808-ad74-4e7e-a0fa-b0051988702d",
            "uid": "4399da1e-8d90-474f-8db4-bd419637b7dd",
            "is_activate": "true"
        }
        private_key = b"secret"
        return jwt.encode(user_info, private_key, algorithm="HS256")
