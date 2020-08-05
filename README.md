# Cloud Functions para extracción de caracterísitcas y entrenamiento de modelo de reconocimiento de actividades

## Funciones

- `initiate_data_processing`(**Cloud Storage**): obtención de datos de nuevo fichero
```
gcloud functions deploy initiate_data_processing --region europe-west1 --runtime python37 --trigger-resource activity-detection-55cc7.appspot.com --trigger-event google.storage.object.finalize
```
- `perform_feature_extraction`(**Pub/Sub**): extracción de características
```
gcloud functions deploy perform_feature_extraction --region europe-west1 --runtime python37 --trigger-topic new-data
```

