"""Configuration settings for Application API"""

import os

from dotenv import load_dotenv

load_dotenv()

# Define ML configurations:
VALIDATION_PCNT = os.environ.get("VALIDATION_PCNT", 0.2)
BATCH_SIZE = os.environ.get("BATCH_SIZE", 128)
IMAGE_WIDTH = os.environ.get("IMAGE_WIDTH", 256)
IMAGE_HEIGHT = os.environ.get("IMAGE_HEIGHT", 192)

# Model metadata:
MODEL_NAME = os.environ.get("MODEL_NAME", "spice_model")
MODEL_STAGE = os.environ.get("MODEL_STAGE", "Production")

# OCR tresholds:
OCR_TRESHOLD = os.environ.get("OCR_TRESHOLD", 0.5)
LEVENSHTEIN_TRESHOLD = os.environ.get("LEVENSHTEIN_TRESHOLD", 3)

# API keys:
OPENAI_KEY = os.environ.get("OPENAI_KEY", "")

