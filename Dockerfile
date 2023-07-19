FROM python:3.9

WORKDIR /app
COPY . /app

# Update PIP & install requirements
RUN python -m pip install --upgrade pip

# Install with DOCKER_BUILDKIT caching
# https://pythonspeed.com/articles/docker-cache-pip-downloads/
RUN --mount=type=cache,target=/root/.cache \
    pip install -e .

EXPOSE 8080

# Run the command on container startup
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--reload", "--port", "8080"]
