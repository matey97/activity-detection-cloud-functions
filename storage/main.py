from google.cloud import pubsub_v1

PROJECT_ID = "activity-detection-55cc7"
NEW_RAW_DATA_TOPIC = "new-data"


def handle_storage_uploads(event, context):
    publisher = pubsub_v1.PublisherClient()

    bucket = event['bucket']
    file = event['name']

    if 'RAW_DATA' in file:
        topic_path = publisher.topic_path(PROJECT_ID, NEW_RAW_DATA_TOPIC)
        publisher.publish(topic_path, data=b'new-data', **{'bucket': bucket, 'file': file})
    elif 'TIDY_DATA' in file:
        # TODO: Publish message in topic for training the model with new data
        pass
