from dotenv import load_dotenv
import os

load_dotenv()


def get_current_env():
    return os.getenv("ENV") if os.getenv("ENV") is not None else "dev"


ENVIRONMENT_VARIABLES = {
    "ENV": get_current_env(),
    "BUCKET_RAW": "raw",
    "BUCKET_STAGE": "stage",
    "BUCKET_RES": "res",
    "MINIO_URL": os.getenv("MINIO_URL"),
    "MINIO_ACCESS_KEY": os.getenv("MINIO_ACCESS_KEY"),
    "MINIO_SECRET_KEY": os.getenv("MINIO_SECRET_KEY"),
    "ALLOWED_EXTENSIONS": set(['csv', 'tiff']),
    "MONGO_URL": os.getenv("MONGO_URL"),
    "DB_PREFIX": os.getenv("DB_PREFIX"),
    "MONGO_DB_URI": f"{os.getenv('DB_PREFIX')}db{get_current_env()}"
}


MESSAGE_STATUSES = {
    "PENDING": "pending",
    "RUNNING": "running",
    "COMPLETED": "completed",
    "FAILED": "failed"
}
