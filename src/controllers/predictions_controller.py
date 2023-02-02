from fastapi import Body, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
import src.services.logservice as log
from src.util.http_resolvers import BaseResponse, get_tid
from src.data_service.predictions_service import PredictionsService

router = InferringRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@cbv(router)
class PredictionsController():
    """Making predictions"""

    def __init__(self):
        """Initial shared data"""
        print("init predictions")

    @router.post("/api/predictions/{model_id}")
    def post(self, model_id: str, request_body=Body(), token: str = Depends(oauth2_scheme)):
        """making predictions"""
        log.info("making predictions")
        tid = get_tid(token)
        response = request_body
        response["predictValues"][0]["Prediction"] = "res"
        predictions_service = PredictionsService(
            model_id)
        result = predictions_service.predict_with_data(request_body)
        return BaseResponse.succeed(data=result)
