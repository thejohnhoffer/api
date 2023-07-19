from fastapi import FastAPI, UploadFile, File
from starlette.middleware.cors import CORSMiddleware
from api.utils import read_imagefile

app = FastAPI()

# Enable CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=False,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "DGMD Application APIs"}


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """Provides a class prediction based on uploaded image."""

    # Convert uploaded file into image for prediction:
    # image = read_imagefile(await file.read())

    class_index = "spicy"
    return {"prediction": class_index}
