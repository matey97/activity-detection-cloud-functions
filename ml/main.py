import firebase_admin
from google.cloud import storage
from firebase_admin import ml
import tensorflow as tf
import pandas as pd
from io import StringIO
from sklearn.model_selection import train_test_split


MODEL_NAME = 'activity-recognition'
LABELS_NAME = 'labels.txt'
TFLITE_MODEL = '/tmp/model.tflite'


def train_model(event, context):
    if "attributes" in event:
        attributes = event['attributes']
        bucket = attributes['bucket']
        file = attributes['file']

        firebase_admin.initialize_app(
            credential=firebase_admin.credentials.Certificate('./service_account.json'),
            options={'storageBucket': bucket})

        storage_client = storage.Client()
        storage_bucket = storage_client.get_bucket(bucket)

        features = download_features(storage_bucket.get_blob(file))
        X, Y = create_features_dataframe(features)
        X_train, X_val, Y_train, Y_val = train_test_split(X, Y, test_size=0.3, random_state=53, stratify=Y)

        model_binary = create_model()
        model_binary.fit(X_train, Y_train, batch_size=50, epochs=10, validation_data=(X_val, Y_val))

        save_to_tflite(model_binary, TFLITE_MODEL)
        publish_model_to_firebase(TFLITE_MODEL, MODEL_NAME)


def download_features(blob):
    data = blob.download_as_string()
    return data.decode('utf-8')


def create_features_dataframe(features):
    features_dataframe = pd.read_csv(StringIO(features))
    X = features_dataframe.drop(columns=["CLASS"])
    Y = pd.get_dummies(features_dataframe["CLASS"])
    return X, Y


def create_model():
    model = tf.keras.Sequential(
      [
      tf.keras.layers.Dense(512, activation='relu', input_shape=(29,)),
      tf.keras.layers.Dense(5, activation='softmax')
      ]
    )
    model.summary()

    opt = tf.keras.optimizers.SGD(lr=0.01, decay=1e-6, momentum=0.9)
    model.compile(loss='categorical_crossentropy', optimizer=opt, metrics=['accuracy'])
    return model


def save_to_tflite(model_binary, tflite_model_name):
    converter = tf.lite.TFLiteConverter.from_keras_model(model_binary)
    # converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_model = converter.convert()
    open(tflite_model_name, 'wb').write(tflite_model)


def publish_model_to_firebase(tflite_model_name, model_name):
    source = ml.TFLiteGCSModelSource.from_tflite_model_file(tflite_model_name)
    model_format = ml.TFLiteFormat(model_source=source)
    firebase_models = ml.list_models(list_filter="display_name = {0}".format(model_name)).iterate_all()
    for model in firebase_models:
        custom_model = model

    custom_model.model_format = model_format
    model_to_publish = ml.update_model(custom_model)
    ml.publish_model(model_to_publish.model_id)
