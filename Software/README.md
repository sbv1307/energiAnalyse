# Energimåling - Software

## Issues when porting form x86_64 Linux to armv7l Linux

## Energy-worker module

Based on python, but require redis and postgresq. 

### Dockerfile Raspberry PI Python pip install "PermissionError: [Errno 1] Operation not permitted"

#### First issue:

The python package installer, pip has an issue with the libseccomp2, which is not updated yet for the Raspbian distribution, bun can be downloaded form derbian-backports as a workaround.

```bash

# Get signing keys to verify the new packages, otherwise they will not install
rpi ~$ sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 04EE7237B7D453EC 648ACFD622F3D138

# Add the Buster backport repository to apt sources.list
rpi ~$ echo 'deb http://httpredir.debian.org/debian buster-backports main contrib non-free' | sudo tee -a /etc/apt/sources.list.d/debian-backports.list

rpi ~$ sudo apt update
rpi ~$ sudo apt install libseccomp2 -t buster-backports fails becaue of a missing pgconfig
```

#### Second issue:

The python package installer pip requires an update to installe the redis package.
```bash
RUN pip install --root-user-action=ignore --upgrade pip
```

#### Third issue:

Installation of the python package psycopg2-binary failes due to a missing pg_config program, which isn't installed in the arm32v7/python.

```bash
# Add postgresql-dev gcc python3-dev and musl-dev to the image in the Dockerfile
RUN apk update
RUN apk add postgresql-dev gcc python3-dev musl-dev

```

