from google.cloud import storage, pubsub_v1
from io import StringIO
import pandas as pd
import base64

from feature_extraction import get_features_dataset_from_raw

project_id = "activity-detection-55cc7"
topic_name = "new-data"
tidy_data_path = "TIDY_DATA/{0}_{1}.csv"


def initiate_data_processing(event, context):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_name)

    bucket = event['bucket']
    file = event['name']
    if 'RAW_DATA' in file:
        file_paths = file.split('/')
        activity_type = file_paths[1]
        file_name = file_paths[2]

        storage_client = storage.Client()
        blob = storage_client.get_bucket(bucket).get_blob(file)
        data = blob.download_as_string()

        publisher.publish(topic_path, data=data, **{'file_name': file_name, 'activity_type': activity_type, 'bucket': bucket})


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
