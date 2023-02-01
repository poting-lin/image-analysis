from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel, validator
import re

app = FastAPI()


class InstrumentsRequestModel(BaseModel):
    name: str
    owner: str
    inventoryNumber: str
    instrumentId: Optional[str] = None

    # pylint: disable=no-self-argument
    # pylint: disable=undefined-variable
    @validator(
        "name", "owner", "inventoryNumber"
    )
    def must_no_emoji(cls, value):
        assert re.match(r"^[A-Za-zÀ-ȕ0-9(),-_., +@.|(){}<>!;:.,~!?@#°§$%^=&*]+$",
                        value), f"'{value}' do not match pattern, it allows only letters, umlaut, umbers and special characters"
        assert len(value) >= 3, f"'{value}' must be greater than 3 characters"
        return value


class InstrumentsQueryRequest(BaseModel):
    inventoryNumber: str
    instrumentId: Optional[str] = None

    # pylint: disable=no-self-argument
    # pylint: disable=undefined-variable
    @validator(
        "inventoryNumber"
    )
    def must_no_emoji(cls, value):
        assert re.match(r"^[A-Za-zÀ-ȕ0-9(),-_., +@.|(){}<>!;:.,~!?@#°§$%^=&*]+$",
                        value), f"'{value}' do not match pattern, it allows only letters, umlaut, umbers and special characters"
        assert len(value) >= 3, f"'{value}' must be greater than 3 characters"
        return value
