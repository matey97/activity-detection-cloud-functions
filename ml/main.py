import firebase_admin
from google.cloud import storage
from firebase_admin import ml
import tensorflow as tf

bucket = 'activity-detection-55cc7.appspot.com'


def test_firebase_ml(request):
    firebase_admin.initialize_app(
        credential=firebase_admin.credentials.Certificate('./serviceAccount.json'),
        options={'storageBucket': bucket})

    storage_client = storage.Client()
    storage_bucket = storage_client.get_bucket(bucket)

    ## Check si existe el modelo
    ##   - Si existe cargarlo y entrenar con nuevos datos
    ##   - Si no existe crear uno nuevo y entrenar

    firebase_models = ml.list_models(list_filter="display_name = mi_modelo_pocho").iterate_all()
    custom_model = None
    for model in firebase_models:
        custom_model = model

    if custom_model is not None:
        blob = storage_client.get_bucket(bucket).get_blob('saved_model.h5')
        blob.download_to_filename('/tmp/old_saved_model.h5')

        model_binary = tf.keras.models.load_model('/tmp/old_saved_model.h5')
    else:
        model_binary = tf.keras.models.Sequential(
            [tf.keras.layers.Dense(units=1, input_shape=[1])])
        model_binary.compile(optimizer='sgd', loss='mean_squared_error')

    x = [-1, 0, 1, 2, 3, 4]
    y = [-3, -1, 1, 3, 5, 7]

    model_binary.fit(x, y, epochs=3)

    model_binary.save('/tmp/new_saved_model.h5')
    blob = storage_bucket.blob('saved_model.h5')
    blob.upload_from_filename('/tmp/new_saved_model.h5')

    # TFlite conversion and quantization
    converter = tf.lite.TFLiteConverter.from_keras_model(model_binary)
    #converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_model = converter.convert()
    open('/tmp/modelo_pocho.tflite', 'wb').write(tflite_model)

    # Print input and output shape and type
    # interpreter = tf.lite.Interpreter(model_content=tflite_model)
    # interpreter.allocate_tensors()

    # inputs = interpreter.get_input_details()
    # print('{} input(s):'.format(len(inputs)))
    # for i in range(0, len(inputs)):
    #     print('{} {}'.format(inputs[i]['shape'], inputs[i]['dtype']))

    # outputs = interpreter.get_output_details()
    # print('\n{} output(s):'.format(len(outputs)))
    # for i in range(0, len(outputs)):
    #     print('{} {}'.format(outputs[i]['shape'], outputs[i]['dtype']))

    # Publish model to FirebaseML

    source = ml.TFLiteGCSModelSource.from_tflite_model_file('/tmp/modelo_pocho.tflite')
    model_format = ml.TFLiteFormat(model_source=source)
    if custom_model is not None:
        custom_model.model_format = model_format
        model_to_publish = ml.update_model(custom_model)
    else:
        custom_model = ml.Model(display_name='mi_modelo_pocho', model_format=model_format, tags=["activity_detection"])
        model_to_publish = ml.create_model(custom_model)

    ml.publish_model(model_to_publish.model_id)
