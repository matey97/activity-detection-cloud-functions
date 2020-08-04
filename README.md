# Cloud Functions para extracción de caracterísitcas y entrenamiento de modelo de reconocimiento de actividades

## Funciones

- `get_new_accelerometer_data`(**Cloud Storage**): obtención de datos de nuevo fichero
```
gcloud functions deploy get_new_accelerometer_data --region europe-west1 --runtime python37 --trigger-resource activity-detection-55cc7.appspot.com --trigger-event google.storage.object.finalize
```
- `process_new_data`(**Pub/Sub**): extracción de características
```
gcloud functions deploy process_new_data --region europe-west1 --runtime python37 --trigger-topic new-data
```

