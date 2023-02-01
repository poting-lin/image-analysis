import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.image_etl import controller as EtlController
from src.image_datasets import controller as DatasetsController
from src.image_datasets import list_controller as DatasetsListController
from src.image_predictions import controller as PredictionsController
from src.image_analysis import controller as AnalysisController
from src.image_quality_reports import controller as QualityReportsController
from src.image_quality_reports import list_controller as QualityReportsListController
from src.image_http_health_check import controller as HealthCheckController
from src.image_messages import controller as MessagesController
from src.image_experiments import controller as ExperimentsController
from src.image_experiments import list_controller as ExperimentsListController

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(DatasetsController.router)
app.include_router(DatasetsListController.router)
app.include_router(EtlController.router)
app.include_router(PredictionsController.router)
app.include_router(AnalysisController.router)
app.include_router(QualityReportsController.router)
app.include_router(QualityReportsListController.router)
app.include_router(HealthCheckController.router)
app.include_router(MessagesController.router)
app.include_router(ExperimentsListController.router)
app.include_router(ExperimentsController.router)

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=80,
                log_level="info", reload=True)
