# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.9-slim-buster

# Allow statements and log messages to immediately appear in the Cloud Run logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Install production dependencies.
RUN pip install Flask gunicorn google-cloud-pubsub

# Run the web service on container startup. Here we use the gunicorn production server.
# Because Cloud Run sets the PORT environment variable, we don't need to specify it.
# The `command` tells Cloud Run how to start your application.
# `gunicorn` must be installed prior to this step.
# `app:app` refers to the Flask instance called `app` in `app.py`.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app