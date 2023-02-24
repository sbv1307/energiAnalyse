'''
energy-worker.py

'''
import os
import sys
import psycopg2
import redis
import time

from os.path import exists
from pgConnect import pgConnect
from pgCreateTables import pgCreateTables
from pulseTimeStampHandler import pulseTimeStampHandler
from powerUP_Handler import powerUP_Handler
from pgUpdateMeterCount import pgUpdateMeterCount

def processing_flush(tekst, n, index=5):
    sys.stdout.write("\rProcessing %s %s%s" % (tekst, (n % index)* ".", (index - 1 - (n % index))* " "))
    sys.stdout.write("\rProcessing %s %s" % (tekst, (n % index)* "."))
    sys.stdout.flush()

def knownKeyHandler( key, value):
    s_key = key.decode("utf-8")
#    print(f'Know key: {key}. Value: {value} ')
    return True

def illigalKeyHandler( key, valye):
    print(f'Illigal key: {key}. Value: {value}. Deleting key!')
    x = r.delete(key)
    print(f'Key {key} deleted {x}')

####################################################################################################
############################  M A I N #############################################################

# Creat postgres.ini file from environmentvariables if it does not exist
if (not exists("/usr/src/app/postgres.ini")):

    content = """[postgresql]
host=%s
database=%s
user=%s
password=%s
""" % (os.environ['POSTGRES_HOST'], os.environ['POSTGRES_DB'], os.environ['POSTGRES_USER'], os.environ['POSTGRES_PASSWORD'])

    f = open("postgres.ini", "w")
    f.write(content)

r = redis.Redis( host='redis-db', )
print(f'Connection to redis: {r}')

# Verify connection to Postgres and initialze DB if required.
if pgConnect() is not True:
    print('Creating tables')
    pgCreateTables()


n=0
continue_loop = True
while continue_loop:
    # Get list of available keys in Redis DB
    keylist = r.keys("*")

    # Updating processbar.
    tekst = f'Available keys: {keylist}'
    n += 1
    processing_flush(tekst, n, index=50)
    if (n > 100):
        n = 0
    
    # If there are available keys? Handle each key!
    if len(keylist) > 0:
        for key in keylist:

            # Decode key / value set as strings, as they are stored at bytes in redis
            value = r.get(key).decode("utf-8")
            s_key = key.decode("utf-8")


            if "timestamp" in s_key:
                try:
                    millis = int(value)
#                    print(f'Timestamp for {key} = {millis} ')
                    pulseTimeStampHandler( s_key, value)
                except ValueError:
                    print(f'Value: {value} invalid for key {key}. Deleting key!')

                x = r.delete(key)
#                print(f'Key {key} deleted {x}')

            elif "metercount" in s_key:
                try:
                    metercount = int(value)
#                    print(f'Meter count for {key} = {metercount} ')
                    pgUpdateMeterCount( s_key, value)
                except ValueError:
                    print(f'Value: {value} invalid for key {key}. Deleting key!')

                x = r.delete(key)
#                print(f'Key {key} deleted {x}')

            elif "powerup" in s_key and "true" in value:
                powerUP_Handler()
                x = r.delete(key)

            elif "foo" in s_key or "debug" in s_key:
                knownKeyHandler( key, value)

            elif "stop" in s_key and "true" in value:
                x = r.delete(key)
                print(f'\nSTOP received from webhook. \nSTOP key deleted with {x} as result. \nWorker will abort when no more keys are available!!! ')
                continue_loop = False

            else:
                print(f's_key: {s_key}')
                illigalKeyHandler( key, value)
    if (continue_loop):
        time.sleep(0.1)

