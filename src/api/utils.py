"""Helper/utility functions."""
from io import BytesIO

import numpy as np
from PIL import Image

# import api.settings as settings


def read_imagefile(file) -> Image.Image:
    """Converts UploadFile to Image for prediction processing."""
    image = Image.open(BytesIO(file))

    # image_width = settings.IMAGE_WIDTH
    # image_height = settings.IMAGE_HEIGHT

    image_width = 256
    image_height = 192

    image = np.asarray(image.resize((image_width, image_height)))[..., :3]
    image = np.expand_dims(image, 0)
    image = image / 127.5 - 1.0

    return image
