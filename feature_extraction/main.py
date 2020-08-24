from google.cloud import storage
from extraction_process import get_features_dataset_from_raw
from io import StringIO
import pandas as pd

tidy_data_path = "TIDY_DATA/features.csv"


def perform_feature_extraction(event, context):
    if 'attributes' in event:
        attributes = event['attributes']
        bucket = attributes['bucket']
        file = attributes['file']
        file_path = file.split('/')
        activity_type = file_path[1]
        file_name = file_path[2]

        storage_client = storage.Client()
        storage_bucket = storage_client.get_bucket(bucket)

        new_data = download_file(storage_bucket.get_blob(file))
        df = pd.read_csv(StringIO(new_data))
        df = get_features_dataset_from_raw(df, activity_type)

        existing_features = download_file(storage_bucket.get_blob(tidy_data_path))
        existing_features_df = pd.read_csv(StringIO(existing_features))

        join_dataframe = pd.concat([existing_features_df, df], ignore_index=True)
        csv_string = join_dataframe.to_csv(index=False)

        blob = storage_bucket.blob(tidy_data_path)
        blob.upload_from_string(csv_string, content_type='text/csv')


def download_file(blob):
    data = blob.download_as_string()
    return data.decode('utf-8')
