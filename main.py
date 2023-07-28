import json
import os
import time

import mlflow.keras
import numpy as np
from functools import lru_cache
from fastapi import FastAPI, File, UploadFile, Request
import boto3
from mlflow.tracking import MlflowClient
from starlette.middleware.cors import CORSMiddleware
import easyocr

import api.settings as settings
from api.utils import read_imagefile, split_s3_bucket_key, get_ocr_matches
from api.recipe import spice_to_recipe

app = FastAPI()

# Enable CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=False,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

model = None
reader = None
index2label = {}


@app.on_event("startup")
async def startup_event():
    """Cache model at start-up."""
    try:
        initialize_model()
    except Exception as exc:
        print(str(exc))


def initialize_model():
    """Initialize and cache model data."""

    global model
    global index2label
    global reader

    client = MlflowClient()

    # Initialize model from artifact-store:
    if not model:
        model = mlflow.pyfunc.load_model(
            model_uri=f"models:/{settings.MODEL_NAME}/{settings.MODEL_STAGE}"
        )

    # Get associated model artifacts:
    model_artifact_store = ""
    for mv in client.search_model_versions(f"name='{settings.MODEL_NAME}'"):
        if mv.current_stage == settings.MODEL_STAGE:
            model_artifact_store = os.path.split(mv.source)[0]

    # Load mapping file from artifact store:
    if model_artifact_store:
        label_mapping_file = os.path.join(model_artifact_store, "mapping.json")
        index2label = {}

        client = boto3.client("s3")
        bucket_name, key_name = split_s3_bucket_key(label_mapping_file)
        obj = client.get_object(Bucket=bucket_name, Key=key_name)
        index2label = json.loads(obj["Body"].read().decode("utf-8"))

    # Initialize OCR Reader
    reader = easyocr.Reader(['en'])

@app.get("/")
async def root():
    return {"message": "DGMD Application APIs"}


@app.get("/models/list")
async def list_models():
    """Lists available models registered in MLFlow."""
    client = MlflowClient()
    return client.search_registered_models()


@app.get("/models/load")
async def load_model(model_name: str, model_stage: str):
    """Loads a particular model for application use."""

    global model
    model = mlflow.pyfunc.load_model(model_uri=f"models:/{model_name}/{model_stage}")

    return {"status": "success", "model_name": model_name, "model_stage": model_stage}


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """Provides a class prediction based on uploaded image."""

    # Convert uploaded file into image for prediction:
    f = await file.read()
    image = read_imagefile(f)

    global model
    global index2label
    global reader

    if not model or not index2label:
        initialize_model()

    pred = model.predict(image)
    print(f"Prediction: {pred}")

    class_index = int(np.argmax(pred, axis=1)[0])
    print(f"Class index: {class_index}")

    # Convert index to label if available:
    if index2label:
        class_index = index2label.get(str(class_index), str(class_index))

    # Get OCR labels
    match_list = [index2label[index] for index in index2label]
    ocr_matches = get_ocr_matches( reader, f, match_list )

    print(class_index)
    return {"prediction": class_index, "ocr_matches": ocr_matches}

@app.post("/recipe")
async def recipe(req : Request):
    """Provides a recipe based on suggested spices."""
    req_data = await req.json()
    spices = req_data.get("spices", [])
    openai_key = settings.OPENAI_KEY
    no_recipe = {
        "title": "",
        "recipe": "",
        "spices": spices,
        "ingredients": []
    }
    recipe = (
        no_recipe if len(spices) < 1 else spice_to_recipe(spices, openai_key)
    )

    return recipe 
