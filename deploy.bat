@ECHO OFF
IF "%1"=="storage" (
    cd storage
    gcloud functions deploy handle_storage_uploads --region europe-west1 --runtime python37 --trigger-resource activity-detection-55cc7.appspot.com --trigger-event google.storage.object.finalize
    cd ../
) ELSE IF "%1"=="feature_extraction" (
    cd feature_extraction
    gcloud functions deploy perform_feature_extraction --region europe-west1 --runtime python37 --trigger-topic new-data
    cd ../
) ELSE IF "%1"=="ml" (
    cd ml
    gcloud functions deploy train_model --region europe-west1 --runtime python37 --memory 512MB --trigger-topic start-training
    cd ../
) ELSE (
    ECHO Usage: deploy storage^|feature_extraction^|ml
)
