# Cloud Functions para extracción de caracterísitcas y entrenamiento de modelo de reconocimiento de actividades

## Funciones

- `handle_storage_uploads`(**Cloud Storage**): 
    - Pasa el control a `perform_feature_extraction` si hay un nuevo fichero de lecturas de acelerómetro
    - Pasa el control a `TBD` si hay un nuevo fichero de caracterísitcas
```
gcloud functions deploy handle_storage_uploads --region europe-west1 --runtime python37 --trigger-resource activity-detection-55cc7.appspot.com --trigger-event google.storage.object.finalize
```
- `perform_feature_extraction`(**Pub/Sub**): extracción de características
```
gcloud functions deploy perform_feature_extraction --region europe-west1 --runtime python37 --trigger-topic new-data
```

