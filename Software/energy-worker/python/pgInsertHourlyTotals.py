'''
USAGE:
    pgInsertHourlyTotals()

The function is expected to run every hour, witin the first 5 minues of the hour.
The pgInsertHourlyTotals() function addes kWh'rs for each meter from the meter_status table to the hourly_totals table, 
calculate the difference since last entry, an hour ago and add these informatins aswell.

'''

import psycopg2
import datetime
from datetime import timedelta  

from pgGetTimeStamp import pgGetTimeStamp
from pgGetHourlyTotals import pgGetHourlyTotals


from pgConfig import pgConfig
from pgGetMeterValues import pgGetMeterValues

#
def pgInsertHourlyTotals():
    conn = None

    # For inserts made before 00:05:00 will be set to 00:00:00 
    time_stamp = pgGetTimeStamp()
    date = time_stamp.date()

    time_ref = datetime.time( time_stamp.hour(), 5, 0)

    print(f'Current time: {date} Time reference: {time_ref}')

    if time_stamp.time() < time_ref:
        time = datetime.time( time_stamp.hour(), 0, 0)
        refDate = time_stamp - timedelta(hours=1)
        refDate = refDate.date()
    else:
        time = "{:%H:%M:%S}".format(time_stamp.time())
        refDate = date

    # Get last totalse

    refTime = datetime.time( time_stamp.hour(), 0, 0)
    lastTotals = pgGetHourlyTotals( refDate, refTime)



    # Get current meter kWh'rs from meter_status ordered by meter numer
    meterValues = pgGetMeterValues()

#    updated_rows = None
    
    try:
        # read connection parameters
        params = pgConfig()

        # connect to the PostgreSQL server
        action = "pgInsertHourlyTotals - Connect to PostGres database: "
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()



        # Insert kWh'rs into hourly_totals
        action = "pgInsertHourlyTotals - Insert into hourly_totals: "
        if lastTotals != None:
            insert_stmt = "INSERT INTO hourly_totals (date, time, meter_no_1, meter_no_2, meter_no_3, \
                            meter_no_4, meter_no_5, meter_no_6, meter_no_7, \
                            daily_no_1, daily_no_2, daily_no_3, daily_no_4, daily_no_5, daily_no_6, daily_no_7 ) \
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING index"
            cur.execute(insert_stmt, (date, time, meterValues[0], meterValues[1], meterValues[2], meterValues[3], \
                            meterValues[4], meterValues[5], meterValues[6], \
                            round((float(meterValues[0][0]) - float(lastTotals[0])), 2), round((float(meterValues[1][0]) - float(lastTotals[1])), 2), \
                            round((float(meterValues[2][0]) - float(lastTotals[2])), 2), round((float(meterValues[3][0]) - float(lastTotals[3])), 2), \
                            round((float(meterValues[4][0]) - float(lastTotals[4])), 2), round((float(meterValues[5][0]) - float(lastTotals[5])), 2), \
                            round((float(meterValues[6][0]) - float(lastTotals[6])), 2)))
        else:    
            insert_stmt = "INSERT INTO hourly_totals (date, time, meter_no_1, meter_no_2, meter_no_3, \
                            meter_no_4, meter_no_5, meter_no_6, meter_no_7) \
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING index"
            cur.execute(insert_stmt, (date, time, meterValues[0], meterValues[1], meterValues[2], meterValues[3], meterValues[4], meterValues[5], meterValues[6]))

         # close the communication with the PostgreSQL
        cur.close()

        # commit the changes
        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        print(action, error)

    finally:
        if conn is not None:
            conn.close()
        

if __name__ == '__main__':
    
    pgInsertHourlyTotals()

    print(f'Totals updated')