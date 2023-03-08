# energy-worker

This service only one function, build in python.

The service will read the redis database, and take action according the the Key - Value dataset found.

The main program (energy-worker.py), will be the program, which initialize the environment at startup, and run an infinite loop.

The loop will read Key - Value from the redis database and will handle the following Key - Value sets.

| Keys which include: | Value | Esplanation |
|----|----|----|
| timestamp | 0 - 2^32 | The time in milli secunds received from the Arduino board. |
| metercount | 1 - 9999999 | Setting the Energy meter value. NOTE then value does NOT contain a decimal seberator like ',' or '.'. The two last didgits will be decimals. This is to make data enrty faster and easier. |
| powerup | true | This will start the powerUP_Handler.py module. Because the time on the Arduino server will start over (from 0), when it powers up. Then data handled by the pulseTimeStampHandler.py module will need to be able to handle the comming timestamp - millis key - value sets correctly. The powerUP_Handler.py module does just that. |
| stop | true | When this Key - Value combination is found, the infinite loop will exit, and the container will exit as well. |
| foo | bar | A Key - Valye set, which is used by the debug funktion in the energy-webhook service. No actions taken |
| Every thing else | Any value | Illegal Key - Value combination. Will be deleted |

## The program stack

| module | Function | Arguments | Returns | Description
|----|----|----|----|----|
| energy-worker.py | Main | None | -  | Runs  the infinite loop. Verify redis Key - Value pair and run required process |
| pulseTimeStampHandler.py | pulseTimeStampHandler | Redis key - value pair | -  | Calculate Energy meter counts, kWh and power comsumption. Update respective tables in PostgreSQL for further analysis, done by grafana    |
| pgConfig.py | pgConfig | filename, section   | parameters for psycopg2.connect   | Read the postgres.ini file and returne the parameters used by the pgConnect function |
| pgConnect.py | pgConnect | None   | true / false | Connect to the PostsgreSQL database, and verify if the required tables are avalable |
| pgCreateTables.py | pgCreateTables | None   | -  | Create required tables in the PostgreSQL database. |
| pgGetMeterMetadata.py | pgGetMeterMetadata | Energy meter number |Energy Metadata | Returns meta data.    |
| pgGetMeterStatus.py | gGetMeterStatus | Energy meter number | Data from the meter-status table.   |    |
| pgGetNumberOfRows.py | pgGetNumberOfRows | PostgredSQL table name | Number of rows | Used my index.py to buld the page. |
| pgGetTimeStamp.py | pgGetTimeStamp | None | System time from the PostgreSQL service   | Used for every entry done, as a reference.  |
| pgInsertConsumption.py | pgInsertConsumption | Column Names |    |    |
| pgUpdateComsumption.py | pgUpdateComsumption | Column Names |    |    |
| pgUpdateMeterCount.py | pgUpdateMeterCount  | Column Names |    |    |
| pgUpdateMeterStatus.py | pgUpdateMeterStatus | Column Names |    |    |
| powerUP_Handler.py |    | powerUP_Handler   | None |    |


## energy-worker.py 

The module  equires setting of the following envionrment variables, as it will build the postgres.ini file, used by the pgConfig.py module, to read the PostgreSQL configuration, which the module pgConnect, uses to establish the actual connection to the PostgreSQL database.

````bash
# In docker-compose.yamll file:
environment:
  POSTGRES_USER: <username>                 # Decide you own username
  POSTGRES_PASSWORD: <password>             # Be aware of using special characteres. 
                                            # Special characters might be interpreted in various ways be the OS. 
  POSTGRES_DB: <PostgreSQL database name>   # Decite you own database name
  POSTGRES_HOST: postgres-db                # Do NOT change. Need to med the same as the service name for the postgres image
 
````

## pushToGoogle.py

This module rquires:
- postgres database is accessable, and tables have been created by the pgCeateTabels.py module. (typicaly done when energy-werker.py have been run once.)
- The environmentvariable GOOGLE_WEBHOOK_URL 

````Bash
# In docker-compose.yamll file:
environment:
    GOOGLE_WEBHOOK_URL: <local webhook url e.g. http://192.168.10.102/energyRegistrations/updateEnergyRegistrations>
````

Currently the URL for the google webhook is:
- http://192.168.10.102/energyRegistrations/updateEnergyRegistrations
The request will take the form:                 function=updateSheet&dataString=<Value for meter 1>,<Value for meter 2>,....<Value for meter7>

The resulting GET request will be:
- GET /energyRegistrations/updateEnergyRegistrations?function=updateSheet&dataString=<Value for meter 1>,<Value for meter 2>,....<Value for meter7>

Eksample
 * http://192.168.10.102/energyRegistrations/updateEnergyRegistrations?function=updateSheet&dataString=279.97,752.04,260.03,441.21,806.67,1.08,3362.79


## Comments to the Dockerfile

The program stack requires access to both Redis in-memory data store anb PostgreSQL. 

For the arm32v7/python:3-alpine image, access to Redis was quite simple:

````bash
# In the Docker file include:
RUN pip install --root-user-action=ignore redis
````

However it required a bit more, to get required package for PostgreSQL installed.

Installation of the psycopg2-binary package required a newer version of the pip installer (pip install --root-user-action=ignore --upgrade pip)

The actual installation of the psycopg2-binary it self, required tthe following pachages to be installed (ostgresql-dev gcc python3-dev musl-dev)

````bash
# IN the Dockerfile the following lines will install the required pachages for Radis and PostgreSQL
RUN apk update
RUN apk add postgresql-dev gcc python3-dev musl-dev

# Install 
RUN pip install --root-user-action=ignore --upgrade pip
RUN pip install --root-user-action=ignore redis
RUN pip install --root-user-action=ignore psycopg2-binary
````

## ISSUES

### Issue #1 - Solved - energy-worker.py changed to handle a situation, where the PostgreSQL database is not ready.

Eenergy-worker fails to start at the initial run. After taking the program stack down (docker-compose down), and bring it up again sovled the issue sosmetimes..
It has turned out, that the postgres-db service has not finished setting op the PostgreSQL database, and made it ready for connections. This process takes several minutes (meaured once to 3.5 minues).

### Issue #2 - Solved - postgres.ini now saved in /etc

Relocate postgress.ini file to the "standard" location for configuration files. Til will avoid postgres.ini from being imported from the develup enviornnment.
https://stackoverflow.com/questions/1024114/location-of-ini-config-files-in-linux-unix

