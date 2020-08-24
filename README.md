# Cloud Functions para extracción de caracterísitcas y entrenamiento de modelo de reconocimiento de actividades

## Introducción
Este repositorio contiene [**Cloud Functions**](https://cloud.google.com/functions) desplegadas en **Google Cloud Platform**
que permiten la extracción de caracterísitcas de datos de acelerometro en crudo y su posterior uso para el entrenamiento
de un modelo de Machine Learning para el reconocimiento de actividades de forma completamente automatizada. Los datos de 
acelerómetro son recogidos por el usuario empleando al aplicación Android [**ActivityRecorder**](https://github.com/matey97/ActivityRecorder) 
y son guardados automáticamente en [**Cloud Storage**](https://firebase.google.com/products/storage). 

Al almacenarse un fichero en el **Cloud Storage**, se lanza la función `handle_storage_uploads`, la cual determina el tipo de fichero
que se ha almacenado (datos en crudo, fichero de características, etc.) y publica un mensaje en un determinado tópico
de [**Pub/Sub**](https://cloud.google.com/pubsub) para lanzar otra función y actuar en consecuencia.

Cuando el fichero almacenado se corresponde con un fichero de datos en crudo de acelerometro, se lanza la función 
`perform_feature_extraction`, la cual extrae las características de los datos en crudo y las alamcena en otro 
fichero en **Cloud Storage**

Cuando el fichero almacenado se corresponde con un fichero de características, se lanza la función `train_model`, la cual 
emplea dichas caracteristicas para entrenar un modelo de Machine Learning y publicarlo en 
[**Firebase Machine Learning**](https://firebase.google.com/docs/ml) para su posterior uso en dispositivos móviles.

## Funciones

- `handle_storage_uploads`(**Cloud Storage**): 
    - Pasa el control a `perform_feature_extraction` si hay un nuevo fichero de lecturas de acelerómetro
    - Pasa el control a `train_model` si hay un nuevo fichero de caracterísitcas
```
gcloud functions deploy handle_storage_uploads
    --region europe-west1 
    --runtime python37 
    --trigger-resource activity-detection-55cc7.appspot.com
    --trigger-event google.storage.object.finalize
```
- `perform_feature_extraction`(**Pub/Sub**): extracción de características
```
gcloud functions deploy perform_feature_extraction
    --region europe-west1
    --runtime python37 
    --trigger-topic new-data
```
- `train_model` (**Pub/Sub**): entrenamiento y publicación del modelo de Machine Learning
```
gcloud functions deploy train_model
    --region europe-west1
    --runtime python37 
    --memory 512MB
    --trigger-topic start-training
```
