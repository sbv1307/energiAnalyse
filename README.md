# Energi analyse

Registrerer pulser på syv energimålere og sender Ardhino timestamp videre til 

## **Usage**

## **Requirements**

- Raspberry Pi model B v1.2. Installed with Raspberry Pi OS Lite (32-bit) <span id="a1">[[1]](#f1)</span>.
- Internet access and attached to the DMZ.
- Docker Engin and Docker Compose installed <span id="a2">[[2]](#f2)</span>.

## **Installation**

- Login as pi
- Create direcoty: energiAnalyse

### **Create docker-compose file**

In folder `energiAnalyse` create file `docker-compose.yaml`

```bash
vi docker-compose.yaml
```

Add the following contend:

```bash
# Docker-compose file for building the "Energianalyse" program stack.

version: '3.8'

# Configual parameters for the services. This is just a way to group these settings an mage changes easy
# POSTGRES... environemtn variables are used in the postgres-db, energy-webhook and energy-worker services.
# DATABASE... environment variables are used in the grafana service
x-environment: &enviroment_vars
  POSTGRES_USER: energy                 # Decide you own username
  POSTGRES_PASSWORD: energy             # Be aware of using special characteres.
                                        # Special characters might be interpreted in various ways be the OS. 
  POSTGRES_DB: energy                   # Decite you own database name
  POSTGRES_HOST: postgres-db  # Do not change. Need to med the same as the service name for the postgres image

  DATABASE_USER: energy                 # Specify the same name as for POSTGRES_USER
  DATABASE_PASS: energy                 # Specify the same name as for POSTGRES_PASSWORD
  DATABASE_NAME: energy                 # Specify the same name as for POSTGRES_DB
  DATABASE_HOST: postgres-db  # Do not change. Need to med the same as the service name for the postgres image

  GOOGLE_WEBHOOK_URL: http://192.168.10.102/energyRegistrations/updateEnergyRegistrations
  GOOGLE_WEBHOOK: test

services:
  redis-db:
    image: arm32v7/redis
    restart: always
    container_name: redis-db
    networks:
      - front-end
      - back-end
    volumes:
      - redis-data:/data

  postgres-db:
    image: postgres
    restart: always
    container_name: postgres-db
    networks:
      - front-end
      - back-end
    environment: *enviroment_vars
    volumes:
      - energy-db:/var/lib/postgresql/data

  adminer:
    image: adminer
    restart: always
    container_name: postgres-adm
    ports:
      - 8080:8080
    networks:
      - back-end

  mosquitto-mqtt:
    container_name: mosquitto-mqtt
    image: eclipse-mosquitto:2
    restart: always
    command: mosquitto -c /mosquitto-no-auth.conf
    ports:
      - 1883:1883
    volumes:
      - mosquitto-conf:/mosquitto/config
      - mosquitto-data:/mosquitto/data
      - mosquitto-log:/mosquitto/log
    networks:
      - front-end

  energy-webhook:
    container_name: energy-webhook
    image: sbv1307/energy-webhook
    restart: always
    environment: *enviroment_vars
    links:
      - redis-db
    ports:
      - 8880:80
    depends_on:
      - redis-db
      - energy-worker
      - mosquitto-mqtt
    networks:
      - front-end

  energy-mqtthook:
    container_name: energy-mqtthook
    image: energy-mqtthook
    restart: always
    environment:      # Set environment variables: Se more info in main README.md
      - MAIL_SMTP_HOST=${MAIL_SMTP_HOST}
      - MAIL_SMTP_USERNAME=${MAIL_SMTP_USERNAME}
      - MAIL_SMTP_PASSWORD=${MAIL_SMTP_PASSWORD}
    links:
      - redis-db
    depends_on:
      - redis-db
      - energy-worker
      - mosquitto-mqtt
    networks:
      - front-end
    
  energy-worker:
    container_name: energy-worker
    image: sbv1307/energy-worker 
    restart: always
    environment: *enviroment_vars
    links:
      - redis-db
      - postgres-db
    depends_on:
      - redis-db
      - postgres-db
    networks:
      - back-end

  grafana:
    container_name: grafana
    image: grafana/grafana
    restart: always
    environment: *enviroment_vars
    volumes:
      - energy-grafana-data:/var/lib/grafana
    ports:
      - 3500:3000
    depends_on:
      - postgres-db
    networks:
      - back-end
      

networks:
  front-end:
    name: Fron-end
  back-end:
    name: back-end

volumes:
  redis-data:
    name: redis-data
  energy-grafana-data:
    name: grafana-data
  energy-db:
    name: energy-db
  mosquitto-conf:
    name: mosquitto-conf
  mosquitto-data:
    name: mosquitto-data
  mosquitto-log:
    name: mosquitto-log


```

Before starting the docker container, set the following environment variables in the system on which the docker container will run - Remember to export the environmentvariables:
 
 ````bash
MAIL_SMTP_HOST=*smtp server name* # e.g. smtp.gmail.com
export MAIL_SMTP_HOST
MAIL_SMTP_USERNAME=*SMTP username*  # typically an e-mail address.
export MAIL_SMTP_USERNAME
MAIL_SMTP_PASSWORD=*SMTP password*
export MAIL_SMTP_PASSWORD

 ````
 
 S tart the docker container with `docker-compose up -d`.

```bash
docker-compose up -d
```

#### For debugging and developnemt insert

```bash
  energy-webhook:
    .
    .
    volumes:      #v Verify that this is located under the energy-webhook service !
      - ./energy-webhook/www:/var/www/html

  energy-worker:
    .
    .
    volumes:      #v Verify that this is located under the energy-worker service !
      - ./energy-worker/python:/usr/src/app

  energy-mqtthook:
    .
    .
    volumes:    # Verify that his i located under the energy-mqtthook service !!!!!
      - ./energy-mqtthook/usr/src/mqtt:/usr/src/mqtt

  
```



#### **Footnotes**
=======
###### 1. <span id="f1"></span> See document: [Setting up and configure Raspberry Pi 3 MODEL B+ for the energy analasys project](./docs/SettingUpRaspberryPi.md). [$\hookleftarrow$](#a1)

###### 2. <span id="f2"></span> See document [Install Docker Engin and Docker Compose](./docs/InstallDockerEnginAndCompose.md)[$\hookleftarrow$](#a3)

