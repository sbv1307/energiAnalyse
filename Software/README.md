# Energimåling - Software

## **Issues**

- From *docker-compose logs -f* at *docker-compose up -d* 

````bash
 redis-db           | 1:M 02 Apr 2023 04:11:51.294 # WARNING Memory overcommit must be enabled! Without it, a background save or replication may fail under low memory condition. Being disabled, it can can also cause failures without low memory condition, see https://github.com/jemalloc/jemalloc/issues/1328. To fix this issue add 'vm.overcommit_memory = 1' to /etc/sysctl.conf and then reboot or run the command 'sysctl vm.overcommit_memory=1' for this to take effect.

 energy-webhook     | AH00558: apache2: Could not reliably determine the server's fully qualified domain name, using 192.168.96.5. Set the 'ServerName' directive globally to suppress this message

````

energy-webhook issue - SOLVED: the following has been added to dockerfile:

````bash
RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf
````

## Issues when porting form x86_64 Linux to armv7l Linux

## Energy-worker module

Based on python, but require redis and postgresq. 

### Dockerfile Raspberry PI Python pip install "PermissionError: [Errno 1] Operation not permitted"

#### First issue

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

## Software Version History

3.0.2 - Initial version. Previous versions were unmanaged. 
3.0.3 - Tinezone added to the energy-worker image.

### Issue #1 Solved

Version 3.0.2: Push To Google. Before the current energy registration can be removed, it's required to be able to proceed sending daily reports to google.

1 - Add a ´"post to Google" function to webhook.  Solved
2 - Add a table to PostgreSQL to collect energy meter totals (a kind of copy of the Google Sheet)

### Issue #2 - Solved

README.md files for energy-webhook and -worker relocated, so they get copied to the docker image - this will reflect which verion is installed in the docker image.

### Issue #3 - Solved

The cron job, which runs "post to Google" and opdate the Energy Meters Total tabel runs in UTC and not CET.
Time Zone need to be added. 