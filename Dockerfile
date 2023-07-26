FROM python:3.8-slim-buster

WORKDIR /app
COPY . /app

# Update PIP & install requirements
RUN python -m pip install --upgrade pip
RUN pip install -e .

EXPOSE 8080

# Run the command on container startup
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--reload", "--port", "8080"]
