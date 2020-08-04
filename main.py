from google.cloud import storage, pubsub_v1
from io import StringIO
import pandas as pd
import base64

from feature_extraction import get_features_dataset_from_raw

project_id = "activity-detection-55cc7"
topic_name = "new-data"
tidy_data_path = "TIDY_DATA/{0}_{1}.csv"


def get_new_accelerometer_data(event, context):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_name)

    bucket = event['bucket']
    file = event['name']
    if 'RAW_DATA' in file:
        activity_type = file.split('/')[1]

        storage_client = storage.Client()
        blob = storage_client.get_bucket(bucket).get_blob(file)
        data = blob.download_as_string()

        publisher.publish(topic_path, data=data, **{'activity_type': activity_type, 'bucket': bucket})


def process_new_data(event, context):
    if 'data' in event:
        data = base64.b64decode(event['data']).decode('utf-8')
        attributes = event['attributes']
        activity_type = attributes['activity_type']

        df = pd.read_csv(StringIO(data))
        df = get_features_dataset_from_raw(df, 10, 5, activity_type)

        csv_string = df.to_csv(index=False)

        storage_client = storage.Client()
        bucket = storage_client.get_bucket(attributes['bucket'])
        blob = bucket.blob(tidy_data_path.format(activity_type, context.timestamp))
        blob.upload_from_string(csv_string, content_type='text/csv')
