from google.cloud import storage, pubsub_v1

project_id = "activity-detection-55cc7"
topic_name = "new-data"


def handle_storage_uploads(event, context):
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

        # TODO: Do not send the data in de message, just send the attributes and let the other function to retrieve de data
        publisher.publish(topic_path, data=data, **{'file_name': file_name, 'activity_type': activity_type, 'bucket': bucket})
