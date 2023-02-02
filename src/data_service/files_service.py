from minio import Minio
from werkzeug.utils import secure_filename

from src.data_repository.files_repository import FileRepository
import src.services.logservice as log
from src.config import ENVIRONMENT_VARIABLES


class FileService():
    def __init__(self):
        """Initial shared data"""
        self.client = Minio(ENVIRONMENT_VARIABLES["MINIO_URL"],
                            access_key=ENVIRONMENT_VARIABLES["MINIO_ACCESS_KEY"],
                            secret_key=ENVIRONMENT_VARIABLES["MINIO_SECRET_KEY"],
                            secure=True)

    def get_filelist_datasets(self, dataset_id: str = None):
        """Get list of dataset files from API"""
        # List all object paths in bucket that begin with my-prefixname.
        if dataset_id is None:
            folder_name = ""
        else:
            folder_name = f"{dataset_id}/"
        try:
            objects = self.client.list_objects(
                ENVIRONMENT_VARIABLES["BUCKET_RAW"], prefix=folder_name, recursive=True)
        except Exception as exception:
            return f"get list failed: {exception}"

        dataset_list = []
        for obj in objects:
            print(obj.bucket_name, obj.object_name.encode('utf-8'),
                  obj.last_modified, obj.etag, obj.size, obj.content_type)
            dataset_list.append({
                "path": str(obj.object_name),
                "etag": str(obj.etag),
                "lastModified": str(obj.last_modified),
                "isDir": obj.is_dir,
                "size": obj.size,

            })
        return dataset_list

    def create_bucket(self, bucket_name):
        # Create bucket.
        self.client.make_bucket(bucket_name)

    def check_bucket(self, bucket_name) -> bool:
        if self.client.bucket_exists(bucket_name):
            log.info(f"{bucket_name} exists")
            return True
        else:
            log.warning(f"{bucket_name} does not exist")
            return False

    def upload_files(self, files: list, dataset_id: str):
        """Upload file to minio"""
        file_list = []
        for file in files:
            contents = file.file.read()
            filename = secure_filename(file.filename)

            uploaded_file = FileRepository(filename, contents)
            uploaded_file.write()

            if not uploaded_file.file_fullpath:
                # TODO: ask BE to get standard error message format
                error_message = "temp file creation failed."
                log.error(error_message)
                raise RuntimeError(error_message)

            if self.check_bucket(ENVIRONMENT_VARIABLES["BUCKET_RAW"]) is False:
                self.create_bucket(ENVIRONMENT_VARIABLES["BUCKET_RAW"])

            try:
                result = self.client.fput_object(
                    ENVIRONMENT_VARIABLES["BUCKET_RAW"],
                    f"{dataset_id}/{filename}",
                    uploaded_file.file_fullpath)
                print(
                    f"created {result.object_name} object; etag: {result.etag}, version-id: {result.version_id}")
            except Exception as exception:
                raise RuntimeError(exception) from exception
            file_list.append(filename)
        return file_list

    def validate_file_extension(self, files: list) -> dict:
        # check if file extension is allowed
        errors = {}
        success = {}
        all_validated = False
        for file in files:
            if file and self.allowed_file(file.filename):
                success[file.filename] = "Validated"
                all_validated = True
            else:
                errors[file.filename] = "File type is not allowed"
                all_validated = False

        response = {
            "success": success,
            "error": errors,
            "all_validated": all_validated
        }
        return response

    def allowed_file(self, filename) -> bool:
        # Determine if the file extension is allowed
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ENVIRONMENT_VARIABLES["ALLOWED_EXTENSIONS"]
