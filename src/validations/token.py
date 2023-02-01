import jwt
from typing import Optional
from flask import abort
from http import HTTPStatus


class Token:
    """Parsing token from request."""

    def __init__(self, bearer: Optional[str], property_data: str):
        self.bearer = bearer
        self.property = property_data

    def get_property(self):
        if not self.bearer:
            raise ValueError(f"Token not found, {self.property} not found")

        bearers = self.bearer.split(" ")

        if bearers == None or len(bearers) < 2 or bearers[1] is None:
            raise ValueError(f"Invalid token, {self.property} not found")

        jwt_decoded = jwt.decode(bearers[1], options={"verify_signature": False})
        return jwt_decoded

    def get_tenantId(self):
        try:
            tid = self.get_property()[self.property]
        except ValueError as exception:
            abort(HTTPStatus.BAD_REQUEST, exception)
        except Exception as exception:
            abort(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                exception,
            )
        if tid:
            return tid
