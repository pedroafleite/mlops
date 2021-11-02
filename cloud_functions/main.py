import numpy as np
import pandas as pd
import os
import pickle
from google.cloud import storage

model = None


def download_model_file():

    from google.cloud import storage

    BUCKET_NAME = ""
    PROJECT_ID = "mlops-1635587444840"
    GCS_MODEL_FILE = "model.pkl"

    client = storage.Client(PROJECT_ID)
    bucket = client.get_bucket(BUCKET_NAME)
    blob = bucket.blob(GCS_MODEL_FILE)
    
    folder = '/tmp/'
    if not os.path.exists(folder):
        os.makedirs(folder)
    blob.download_to_filename(folder + "local_model.pkl")


def iris_predict(request):
    global model

    if not model:
        download_model_file()
        model = pickle.load(open("/tmp/local_model.pkl", 'rb'))
    params = request.get_json()

    if (params is not None) and ('features' in params):
        # Run a test prediction
        pred_species  = model.predict(np.array([params['features']]))
        return pred_species[0]        
    else:
        return "nothing sent for prediction"
