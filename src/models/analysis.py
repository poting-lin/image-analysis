from pydantic import BaseModel
from uuid import UUID


class AnalysisRequest(BaseModel):
    modelId: UUID
    datasetId: UUID
