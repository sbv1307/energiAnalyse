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

# Install requests package. Used by pushToGoogle module
RUN pip install --root-user-action=ignore requests

# Too many issues installing python packages for redis and postgresql to use installation based on a requirements file.
# COPY requirements.txt ./
# RUN pip install --no-cache-dir -r requirements.txt

RUN cp /usr/share/zoneinfo/Europe/Copenhagen /etc/localtime
RUN echo "Europe/Copenhagen" >  /etc/timezone

COPY ./python/*.py /usr/src/app/
COPY ./python/crontab.root .
COPY ./python/README.md .

RUN chmod 0744 crontab.root
RUN crontab crontab.root

CMD [ "/bin/sh", "-c", "crond; python energy-worker.py" ]
