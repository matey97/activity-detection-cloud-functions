import firebase_admin
from firebase_admin import ml
import tensorflow as tf

bucket = 'activity-detection-55cc7.appspot.com'


def test_firebase_ml(request):
    firebase_admin.initialize_app(
        credential=firebase_admin.credentials.Certificate('./serviceAccount.json'),
        options={'storageBucket': bucket})

    ## Check si existe el modelo
    ##   - Si existe cargarlo y entrenar con nuevos datos
    ##   - Si no existe crear uno nuevo y entrenar

    x = [-1, 0, 1, 2, 3, 4]
    y = [-3, -1, 1, 3, 5, 7]

    model_binary = tf.keras.models.Sequential(
        [tf.keras.layers.Dense(units=1, input_shape=[1])])
    model_binary.compile(optimizer='sgd', loss='mean_squared_error')
    model_binary.fit(x, y, epochs=3)

    source = ml.TFLiteGCSModelSource.from_keras_model(model_binary, '/tmp/modelo_pocho.tflite')
    model_format = ml.TFLiteFormat(model_source=source)
    model_1 = ml.Model(display_name='mi_modelo_pocho', model_format=model_format)
    firebase_model_1 = ml.create_model(model_1)
    firebase_model_1 = ml.publish_model(firebase_model_1.model_id)
