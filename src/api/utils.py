"""Helper/utility functions."""
from io import BytesIO

import numpy as np
from PIL import Image
from itertools import product
from Levenshtein import distance


import api.settings as settings


def read_imagefile(file) -> Image.Image:
    """Converts UploadFile to Image for prediction processing."""
    image = Image.open(BytesIO(file))

    image_width = settings.IMAGE_WIDTH
    image_height = settings.IMAGE_HEIGHT

    image = np.asarray(image.resize((image_width, image_height)))[..., :3]
    image = np.expand_dims(image, 0)
    image = image / 127.5 - 1.0

    return image

def parse_box(box):
    return np.round(box).astype(int).tolist()

def get_ocr_matches( reader, img, spice_list ):
    # Format the full OCR result information
    results = reader.readtext(img)
    ocr_raw = [
        { "text": str(r[1]).lower(), "box": parse_box(r[0]), "score": float(r[2]) }
        for r in results
    ]

    text_matches = {}

    # Map any predicted text to nearest valid spice
    for (read, match) in product(ocr_raw, spice_list):
        if distance(read["text"], match) <= settings.LEVENSHTEIN_TRESHOLD:
            text_matches[read["text"]] = match

    # Include the valid spices and distance score
    ocr_all = [
        {"match": text_matches.get(d["text"], None), **d} for d in ocr_raw
    ]

    # Filter by OCR score and text distance
    ocr_matches = [
        d["match"] for d in ocr_all if d["match"] is not None
        and d["score"] >= settings.OCR_TRESHOLD
    ]

    return {
        "ocr_matches": ocr_matches,
        "ocr_all_results": ocr_all,
        "ocr_threshold": settings.OCR_TRESHOLD,
        "levenshtein_threshold": settings.LEVENSHTEIN_TRESHOLD,
    }



def split_s3_bucket_key(s3_path):
    """Split s3 path into bucket and key prefix.
    This will also handle the s3:// prefix.
    :return: Tuple of ('bucketname', 'keyname')
    """
    if s3_path.startswith("s3://"):
        s3_path = s3_path[5:]
    return find_bucket_key(s3_path)


def find_bucket_key(s3_path):
    """
    This is a helper function that given an s3 path such that the path is of
    the form: bucket/key
    It will return the bucket and the key represented by the s3 path
    """
    s3_components = s3_path.split("/")
    bucket = s3_components[0]
    s3_key = ""
    if len(s3_components) > 1:
        s3_key = "/".join(s3_components[1:])
    return bucket, s3_key
