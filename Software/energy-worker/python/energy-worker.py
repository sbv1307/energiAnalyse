'''
energy-worker.py

'''
import os
import psycopg2
import redis
import time

from os.path import exists
from pgConnect import pgConnect
from pgCreateTables import pgCreateTables
from pulseTimeStampHandler import pulseTimeStampHandler
from powerUP_Handler import powerUP_Handler
from pgUpdateMeterCount import pgUpdateMeterCount
from pushToGoogle import pushToGoogle
from pgInsertTotals import pgInsertTotals

def knownKeyHandler( key, value):
    s_key = key.decode("utf-8")
#    print(f'Know key: {key}. Value: {value} ')
    return True

def illigalKeyHandler( key, valye):
#    print(f'Illigal key: {key}. Value: {value}. Deleting key!')
    x = r.delete(key)
#    print(f'Key {key} deleted {x}')

####################################################################################################
############################  M A I N #############################################################

# Print startup info til boot log
print('Starting energy-worker version 2.0.0 - Initial version after version controle')

# Creat postgres.ini file from environmentvariables if it does not exist
if (not exists("/etc/postgres.ini")):

    content = """[postgresql]
host=%s
database=%s
user=%s
password=%s
""" % (os.environ['POSTGRES_HOST'], os.environ['POSTGRES_DB'], os.environ['POSTGRES_USER'], os.environ['POSTGRES_PASSWORD'])

    f = open("/etc/postgres.ini", "w")
    f.write(content)
    f.close()
    
# Set the flag for run the infinite loop 
continue_loop = True

r = redis.Redis( host='redis-db', )
print(f'Connection to redis: {r}')

# Verify connection to Postgres and initialze DB if required.
if pgConnect() is not True:
    
    n = 0    
    while pgConnect() is None and n < 15:
        print('energy-worker - Connect to PostgreSQL database - Try again in 30 sec.')
        time.sleep(30)
        n += 1
    
    if n >= 15:
        print('energy-worker - Giving up connecting to PostgreSQL database ==> ABORTING.')
        continue_loop = False
    elif pgConnect() is not True:
        print('energy-worker - Creating tables in PostgreSQL database')
        if pgCreateTables() is not True:
            print('energy-worker - Creating tables in PostgreSQL database failed ==> ABORTING')
            continue_loop = False

print ('energy-worker - connected to PostfreSQL. Enter infinite loop..')            
n=0
debug = False
while continue_loop:
    # Get list of available keys in Redis DB
    keylist = r.keys("*")

    # If there are available keys? Handle each key!
    if len(keylist) > 0:
        for key in keylist:
            # Decode key / value set as strings, as they are stored at bytes in redis
            value = r.get(key).decode("utf-8")
            s_key = key.decode("utf-8")


            if "timestamp" in s_key:
                try:
                    millis = int(value)
                    if debug:
                        print(f'Timestamp for {key} = {millis} ')
                    pulseTimeStampHandler( s_key, value)
                except ValueError:
                    print(f'Value: {value} invalid for key {key}. Deleting key!')

                x = r.delete(key)
                if debug:
                    print(f'Key {key} deleted {x}')

            elif "metercount" in s_key:
                try:
                    metercount = int(value)
                    if debug:
                        print(f'Meter count for {key} = {metercount} ')
                    pgUpdateMeterCount( s_key, value)
                except ValueError:
                    print(f'Value: {value} invalid for key {key}. Deleting key!')

                x = r.delete(key)
                if debug:
                    print(f'Key {key} deleted {x}')

            elif "pushtogoogle" in s_key and "true" in value:
                pushToGoogle()
                pgInsertTotals()
                x = r.delete(key)

            elif "powerup" in s_key and "true" in value:
                powerUP_Handler()
                x = r.delete(key)

            elif "foo" in s_key:
                knownKeyHandler( key, value)

            elif "debug" in s_key:
                if "true" in value:
                    debug = True
                else:
                    debug = False
                    x = r.delete(key)
                    print(f'Key {key} deleted {x}')

            elif "stop" in s_key and "true" in value:
                x = r.delete(key)
                print(f'\nSTOP received from webhook. \nSTOP key deleted with {x} as result. \nWorker will abort when no more keys are available!!! ')
                continue_loop = False

            else:
                print(f's_key: {s_key}')
                illigalKeyHandler( key, value)
    if (continue_loop):
        time.sleep(0.1)

print("Worker has exited!")

