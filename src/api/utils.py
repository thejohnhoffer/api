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

def get_ocr_matches( reader, img, match_list ):
    results = reader.readtext(img)
    
    # Filter by OCR_Threshold:
    results = [ str(result[1]).lower() for result in results if float(result[2]) >= settings.OCR_TRESHOLD ]

    return [
        pair[0]
        for pair
        in product( match_list, results )
        if distance( pair[0], pair[1]) <= settings.LEVENSHTEIN_TRESHOLD
    ]


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
