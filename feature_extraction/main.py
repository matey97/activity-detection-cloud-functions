from google.cloud import storage
from extraction_process import get_features_dataset_from_raw
from io import StringIO
import pandas as pd
import base64

tidy_data_path = "TIDY_DATA/{0}_{1}"


def perform_feature_extraction(event, context):
    if 'data' in event:
        data = base64.b64decode(event['data']).decode('utf-8')
        attributes = event['attributes']
        activity_type = attributes['activity_type']
        file_name = attributes['file_name']

        df = pd.read_csv(StringIO(data))
        df = get_features_dataset_from_raw(df, activity_type)

        csv_string = df.to_csv(index=False)

        storage_client = storage.Client()
        bucket = storage_client.get_bucket(attributes['bucket'])
        blob = bucket.blob(tidy_data_path.format(activity_type, file_name))
        blob.upload_from_string(csv_string, content_type='text/csv')
