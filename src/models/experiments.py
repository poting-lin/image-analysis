from typing import Optional
from pydantic import BaseModel, validator, root_validator
from uuid import UUID
import time
from datetime import datetime
from dateutil import tz


def startat_must_earlier_than_endat(cls, values):
    if not values["startAt"] < values["endAt"]:
        raise ValueError("startAt must be earlier than endAt")
    return values


class ExperimentsRequestModel(BaseModel):
    sampleId: str
    instrumentId: str
    datasetId: Optional[str]
    experimentTitle: str
    researcherName: str
    laboratoryName: str
    startAt: datetime
    endAt: datetime
    lastUpdatedAt: Optional[datetime]

    _validate_datetime = root_validator(allow_reuse=True)(
        startat_must_earlier_than_endat)

    @validator(
        "datasetId",
        "sampleId",
        "instrumentId"
    )
    def must_in_uuid_format(cls, value):
        try:
            UUID(value)
        except ValueError as exception:
            raise ValueError('must in UUID format') from exception
        return value

    @validator(
        "startAt",
        "endAt",
    )
    def convert_to_epoch_time(cls, value):
        if value is not None:
            return value.timestamp()
        return value


class ExperimentsResponseModel(BaseModel):
    experimentId: UUID
    sampleId: str
    instrumentId: str
    datasetId: Optional[str]
    experimentTitle: str
    researcherName: str
    laboratoryName: str
    startAt: datetime
    endAt: datetime
    lastUpdatedAt: Optional[datetime]

    _validate_datetime = root_validator(allow_reuse=True)(
        startat_must_earlier_than_endat)

    @validator(
        "datasetId",
        "sampleId",
        "instrumentId"
    )
    def must_in_uuid_format(cls, value):
        try:
            UUID(value)
        except ValueError as exception:
            raise ValueError('must in UUID format') from exception
        return value

    @validator(
        "startAt",
        "endAt",
        "lastUpdatedAt"
    )
    def convert_to_local_datetime(cls, value):
        if value is not None:
            original_datetime = value.replace(tzinfo=tz.tzutc())
            datetime_convert_to_local = original_datetime.astimezone(
                tz.tzlocal())
            return datetime_convert_to_local.replace(tzinfo=None)
        return value
