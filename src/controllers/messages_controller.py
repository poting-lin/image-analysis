from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
import src.services.logservice as log
from src.util.http_resolvers import BaseResponse
from src.data_service.messages_service import MessagesService

router = InferringRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@cbv(router)
class MessagesController():
    """Making predictions"""

    def __init__(self):
        """Initial shared data"""
        print("init message")

    @router.get("/api/messages")
    def get_all_messages(self, token: str = Depends(oauth2_scheme)):
        """making predictions"""
        log.info("making predictions")
        tid = "f112abc4-d49a-4bc9-a058-ddbe2c0bd2ab"
        uid = "d700bcda-90c9-436e-932b-75174b65f399"
        message_list = MessagesService(tid, uid, "analyses").get_all_messages()
        return BaseResponse.succeed(data=message_list)
