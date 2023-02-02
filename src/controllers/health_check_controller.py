from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
import src.services.logservice as log
from starlette import status
from src.util.http_resolvers import BaseResponse

router = InferringRouter()  # Step 1: Create a router


@cbv(router)
class HealthCheckController():
    @router.get("/api/healthcheck")
    def get_status(self):
        """
        This is the Documents API
        Call this api and get the health check
        ---
        tags:
          - HealthCheck
        parameters:
          - name: throwException
            in: path
            type: string
            required: false
            description: The language name
        responses:
          400:
            description: Error
          200:
            description: OK
            schema:
              type: object
              properties:
                Succeed:
                  type: string
                  description: status
                  default: True
                MissingConfigurations:
                  type: string
                  description: Show the keys missing

        """
        message = "Documents service healthcheck response succeed"
        log.info(message)
        return BaseResponse.succeed(status_code=status.HTTP_200_OK, message=message)
