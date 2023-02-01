import pandas as pd
from minio import Minio
from io import BytesIO


class EtlRepository:
    def __init__(self, minio_url, access_key, secret_key):
        self.client = Minio(minio_url,
                            access_key=access_key,
                            secret_key=secret_key,
                            secure=True)

    def list_objects(self, bucket_name):
        objects = self.client.list_objects(bucket_name)
        for obj in objects:
            print(obj.object_name)

    def download_an_object(self, bucket_name, object_name, file_name):
        # Download data of an object.
        self.client.fget_object(bucket_name, object_name, file_name)

    def download_all_objects(self, bucket_name):
        objects = self.client.list_objects(bucket_name)
        for obj in objects:
            self.download_an_object(
                bucket_name, obj.object_name, obj.object_name)

    def get_an_object(self, bucket_name, object_name):
        try:
            response = self.client.get_object(bucket_name, object_name)
            print(f"reading object: {object_name}")
            return response.data
            # Read data from response.
        finally:
            response.close()
            response.release_conn()

    def get_all_objects(self, bucket_name) -> pd.DataFrame:
        file_name = None
        df = pd.DataFrame(columns=['ImageName', 'IMPARA-AMP_Sa', 'IMPARA-AMP_Sq;IMPARA-AMP_Ssk', 'IMPARA-AMP_Sku',
                                   'IMPARA-AMP_Sz', 'IMPARA-AMP_S10z', 'IMPARA-AMP_Mean', 'MATERIAL_Back', 'MATERIAL_Cont'])
        objects = self.client.list_objects(bucket_name)
        for obj in objects:
            if file_name is None:
                main_file_name = obj.object_name.split("_", 3)
                file_name = f"{main_file_name[0]}_{main_file_name[1]}_{main_file_name[2]}.csv"
            obj_data = self.get_an_object(bucket_name, obj.object_name)
            obj_df = pd.read_csv(BytesIO(obj_data), sep=";",
                                 decimal=",")
            df = pd.concat([df, obj_df])
        # df.to_csv("df_total.csv", index=False)
        return df, file_name

    def upload_object(self, bucket_name, object_name, df):
        # There is a strange bug in set_index. it is functional but show escpetion, so I pass it.
        try:
            df.set_index('ImageName', inplace=True)
        except Exception as e:
            print(e)
            pass
        csv_file = df.to_csv().encode('utf-8')
        try:
            self.client.put_object(bucket_name,
                                   object_name,
                                   data=BytesIO(csv_file),
                                   length=len(csv_file),
                                   content_type='application/csv')
        except Exception as ex:
            print(f"upload object failed: {ex}")
        print("upload object succeed")
