# Dockerfile for energy-worker
FROM arm32v7/python:3-alpine
LABEL Name=arm32v7_Python Version=3.11.1
LABEL Name=arm32v7_redis Version=4.4.0

WORKDIR /usr/src/app
# Installation og psycopg2-binary, used by Python to access PostgreSQL, requires pg_config program, which isn't installed in the official arm32v7/python image
RUN apk update
RUN apk add postgresql-dev gcc python3-dev musl-dev

# Install 
RUN pip install --root-user-action=ignore --upgrade pip
RUN pip install --root-user-action=ignore redis
RUN pip install --root-user-action=ignore psycopg2-binary

# Too many issues installing python packages for redis and postgresql to use installation based on a requirements file.
# COPY requirements.txt ./
# RUN pip install --no-cache-dir -r requirements.txt

COPY ./python .
CMD [ "python", "./energy-worker.py" ]
