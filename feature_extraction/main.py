from google.cloud import storage
from extraction_process import get_features_dataset_from_raw
from io import StringIO
import pandas as pd

tidy_data_path = "TIDY_DATA/{0}/{1}"


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

        blob = storage_bucket.get_blob(file)
        data = blob.download_as_string()
        data = data.decode('utf-8')

        df = pd.read_csv(StringIO(data))
        df = get_features_dataset_from_raw(df, activity_type)

        csv_string = df.to_csv(index=False)

        blob = storage_bucket.blob(tidy_data_path.format(activity_type, file_name))
        blob.upload_from_string(csv_string, content_type='text/csv')
