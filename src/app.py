import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.controllers import etl_controller as EtlController
from src.controllers import datasets_controller as DatasetsController
from src.controllers import datasets_list_controller as DatasetsListController
from src.controllers import predictions_controller as PredictionsController
from src.controllers import analysis_controller as AnalysisController
from src.controllers import quality_reports_controller as QualityReportsController
from src.controllers import quality_reports_list_controller as QualityReportsListController
from src.controllers import health_check_controller as HealthCheckController
from src.controllers import messages_controller as MessagesController
from src.controllers import experiments_controller as ExperimentsController
from src.controllers import experiments_list_controller as ExperimentsListController

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
