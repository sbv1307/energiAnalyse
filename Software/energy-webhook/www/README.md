# energy-webhook

Then main function (in webhook.php) for this service is to catch POST requests, verify these and pass the requests on the the redis database.

It will also accept GET requests, which is mainlly used for debugging.

The fonction (webhook.php) will accept the follwing key - value items:

| Key   | Vaalue       | Key | Value | Function                                   |
|----|----|----|----|-----|
| channel | 1 - 7 | millis | 0 - 2^32 | This request will pass on a channel number (meter number) and a time stamp in milli seconds (produced byt the Ardhino board monitoring the Energy meters) to the redis database. The channel number (1-7) will be incapsulated in a string like: channel:1:timestamp, where '1' is the channel number. |
| channel | metercount |    |    | This request will pass on a channel number (meter number) and a Energy meter value produced by the default function (index.php) to the redis database. The channel number (1-7) will be incapsulated in a string like: channel:1:metercount, where '1' is the channel number. |
| pushtogoogle | true |    |    | Will pass the Key - Value to the redis database. The Energy-worker service will create at GIT request to a webHookServer which will update the Google sheet MeterEnergyRegistrations.
| powerup | true|    |    | This will pass on powerup and true to the redis database. The value (true) has no functionality is just need to be there, to be accepted at a legal request |
| debug | true / false |    |    | Turn output (echo statemenst) on or off. This output will reveal whats received by the webhoog.php function and how these requests are handled.  |
|

## webhook.php

Function to catch POST - and GET requests.

GET requests will be in the form:

host:8880[^1]/webhook.ph?nchannel=1&millis=123456789

host:8880/webhook.ph?nchannel=1&metercount=1234567

host:8880/webhook.ph?powerup=true

host:8880/webhook.ph?powerup=true / host:8880/webhook.ph?powerup=false

## index.php

Function to update Energy meter values.

index.php requires setting of the following envionrment variables:

````bash
# In docker-compose.yamll file:
environment:
  POSTGRES_USER: <username>                 # Decide you own username
  POSTGRES_PASSWORD: <password>             # Be aware of using special characteres. 
                                            # Special characters might be interpreted in various ways be the OS. 
  POSTGRES_DB: <PostgreSQL database name>   # Decite you own database name
  POSTGRES_HOST: postgres-db                # Do NOT change. Need to med the same as the service name for the postgres image
 
````

### Comments to the Dockerfile

Then energy-webhook service is based on arm32v7/php:7.2-apache image.

However the main process (webhook.php) requires access to Redis in-memory data store. As there at no php-redis package available for arm32v7/php:7.2-apache, php-redis will be [installed from sources](https://github.com/phpredis/phpredis/blob/develop/INSTALL.md).

````bash
# In Dockerfile add:
# Install PHP Redis client 
# Installation from sources by git clone https://github.com/phpredis/phpredis.git. Copy files to Docker image and install
WORKDIR /opt/phpredis
COPY ./phpredis .

# Install PHP Redis Client
RUN phpize
RUN ./configure
RUN make install

````

Once php-redis is installed, create a configuration file for the extension and restart PHP.

```bash
# In Docker file add:
WORKDIR /usr/local/etc/php/conf.d
RUN echo "extension=redis.so" > redis.ini

```

default function (indes.php) to get information about the Energy meters, an access to PostgreSQL is required.

It turned out, that there at no PostgreSQL packages availabe for arm32v7/php:7.2-apache, when build in a Docker container.
A solution is to installe a pgsql package using:

```bash
# The pgsql package requires pg_config to install. pg_config is included in libpq-dev.: 
apt-get update && apt-get install libpq-dev -y

# Install pgsql (Requires pg_config to install). 
docker-php-ext-install pgsql -y # 
```

## Version history

### Issue #1 - Solved

index.php - kun meter count and [Opdater] skal have fokus</br>
Solved - Changed input type for meter number from text to hidden

### Issue #2

Adding Send a standard http response header:
        localWebClient.println(P("HTTP/1.1 200 OK"));
        localWebClient.println(P("Content-Type: text/html"));
        localWebClient.println(P("Connnection: close")); // do not reuse connection
        localWebClient.println();


---

[^1]: Portnumber is specified in the docker-compose.yaml file.
