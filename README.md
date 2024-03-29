# Energi analyse

Registrerer pulser på syv energimålere og sender Ardhino timestamp videre til en program stak bygget på docker og afviklet på Raspberry Pi

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

# Generel note aboout environment settings - see README.md file about .env file

version: '3.8'

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
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_HOST=postgres-db   # DO NOT CHANGE!. Need to med the same as the service name for the postgres image
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
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_HOST=postgres-db   # DO NOT CHANGE!. Need to med the same as the service name for the postgres image
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
    image: sbv1307/energy-mqtthook
    restart: always
    environment:
      - MAIL_SMTP_HOST=${MAIL_SMTP_HOST}
      - MAIL_SMTP_USERNAME=${MAIL_SMTP_USERNAME}
      - MAIL_SMTP_PASSWORD=${MAIL_SMTP_PASSWORD}
      - MQTT_SERVER=${MQTT_SERVER}
      - MQTT_PORT=${MQTT_PORT}
      - MQTT_CLIENT_ID=${MQTT_CLIENT_ID}
      - NOTIFICATION_E_MAIL=${NOTIFICATION_E_MAIL}
      - MQTT_POWERUP_NOTIFICATION=${MQTT_POWERUP_NOTIFICATION}
      - MQTT_DISCONNECT_NOTIFICATION=${MQTT_DISCONNECT_NOTIFICATION}
      - MQTT_RECONNECT_NOTIFICATION=${MQTT_RECONNECT_NOTIFICATION}
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
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_HOST=postgres-db   # DO NOT CHANGE!. Need to med the same as the service name for the postgres image
      - GOOGLE_WEBHOOK_URL=${GOOGLE_WEBHOOK_URL}
      - PYTHONUNBUFFERED=1
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
    environment:
      - DATABASE_USER=${POSTGRES_USER}           # Specify the same name as for POSTGRES_USER
      - DATABASE_PASS=${POSTGRES_PASSWORD}       # Specify the same name as for POSTGRES_PASSWORD
      - DATABASE_NAME=${POSTGRES_DB}             # Specify the same name as for POSTGRES_DB
      - DATABASE_HOST=postgres-db  # DO NOT CHANGE!. Need to med the same as the service name for the postgres image
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

Before starting the docker container, create a .env file in the same directory as the docker-compose.yaml file.


```bash
vi .env
```

Add the following contend:


 
 ````bash
POSTGRES_USER=*Username*            # Decide you own username
POSTGRES_PASSWORD=*User password*   # Be aware of using special characteres.
POSTGRES_DB=*Database name*         # Decide you own database name
MAIL_SMTP_HOST=*SMTP hostname*      # For google SMTP: smtp.gmail.com
MAIL_SMTP_USERNAME=*SMTP username*  # Typically an e-mail address
MAIL_SMTP_PASSWORD=*SMTP Password*  #

MQTT_SERVER='mosquitto-mqtt'        # MQTT Broke's hostname or IP Address (here the `mosquitto-mqtt` docker container name is used.)
MQTT_PORT=1883                      # MQTT Broker's port number. TCP/IP port 1883 is reserved with IANA for use with MQTT. 
                                    # TCP/IP port 8883 is also registered, for using MQTT over SSL.
MQTT_CLIENT_ID='webhook-subscriber' # Name used to identify the MQTT client.
NOTIFICATION_E_MAIL=*E-mail addres* # E-mail address to which notifications will be send
# If the one or more of the following environment variables is NOT set, e-mail notificatinos will NOT be send.
MQTT_POWERUP_NOTIFICATION='YES'     # IF set: Energy Meter Powerup notifications will be send. 
MQTT_DISCONNECT_NOTIFICATION='YES'  # IF set: Disconnect notifications will be send
MQTT_RECONNECT_NOTIFICATION='YES'   # IF set: Re-connect  notifications will be send
MQTT_ALIVE_NOTIFICATION=`YES`

GOOGLE_WEBHOOK_URL=*URL for the webhook used by pushToGoogle.py to forward updates to Google sheets*
````

Verify that the environment variables is succesfull read by docker compose.

````bash
docker compose config
````

 Start the docker container with `docker-compose up -d`.

```bash
docker-compose up -d
```

### **For debugging and developnemt insert**

```bash
  energy-webhook:
    .
    .
    volumes:      #v Verify that this is located under the energy-webhook service !
      - ./energy-webhook/www:/var/www

  energy-worker:
    .
    .
    volumes:      #v Verify that this is located under the energy-worker service !
      - ./energy-worker/python:/usr/src/app
    command: sleep 10000  #This will prevent energy-worker.py from starting and keep the container alive for investigation.


  energy-mqtthook:
    .
    .
    volumes:    # Verify that his i located under the energy-mqtthook service !!!!!
      - ./energy-mqtthook/usr/src/mqtt:/usr/src/mqtt
    command: sleep 10000  #This will prevent energy-worker.py from starting and keep the container alive for investigation.
 ```

#### **Usefull aliases**

````bash
alias mountpro="sudo mount.cifs //192.168.n.n/Software /home/pi/energiAnalyse  -o user=IoT password=arduino"
alias dcup='docker-compose up -d'
alias dcdown='docker-compose down'
alias dclogs='docker-compose logs -f'
alias dclogmqtthook='docker logs -f $(docker ps -q --filter "name=energy-mqtthook")'
alias dclogmqtt='docker logs -f $(docker ps -q --filter "name=mosquitto-mqtt")'
alias dockerweb='docker exec -it $(docker ps -q --filter "name=energy-webhook") bash'
alias dockerworker='docker exec -it $(docker ps -q --filter "name=energy-worker") sh'
alias dockerattach='docker attach $(docker ps -q --filter "name=energy-worker")'
alias dockermqtt='docker exec -it $(docker ps -q --filter "name=energy-mqtthook") bash'
````

### **Issues**

- The idea of keeping the logic on the Raspberry Pi and only use the Arduino to colect the time stamps has come too complex - too many processes and too much relaience on network stability.
**Creating a new version 4.0**
- Logging Energy values and comsumption on an hourely basis - Maybe instgead of the current logging, which logs every "blink" at the Energy meters.
- Python app does not print anything when running detached in docker.
  - CMD [ "/bin/sh", "-c", "crond; python energy-worker.py" ]: Currently used.
  - CMD ["python","-u","main.py"] in Docker file, but might not solve the problem
  - PYTHONUNBUFFERED=1 as environment variable. Maybe in combination with PYTHONIOENCODING=UTF-8

- **(ToBe sovled, if it becomes a reald problem)** 
````bash
redis-db           | 1:M 07 Apr 2023 12:32:55.969 # WARNING Memory overcommit must be enabled! Without it, a background save or replication may fail under low memory condition. Being disabled, it can can also cause failures without low memory condition, see https://github.com/jemalloc/jemalloc/issues/1328. To fix this issue add 'vm.overcommit_memory = 1' to /etc/sysctl.conf and then reboot or run the command 'sysctl vm.overcommit_memory=1' for this to take effect.
````


#### **Footnotes**
=======
###### 1. <span id="f1"></span> See document: [Setting up and configure Raspberry Pi 3 MODEL B+ for the energy analasys project](./docs/SettingUpRaspberryPi.md). [$\hookleftarrow$](#a1)

###### 2. <span id="f2"></span> See document [Install Docker Engin and Docker Compose](./docs/InstallDockerEnginAndCompose.md)[$\hookleftarrow$](#a3)

