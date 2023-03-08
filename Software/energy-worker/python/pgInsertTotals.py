'''
USAGE:
    pgInsertTotals()

The pgInsertTotals() function addes kWh'rs for each meter from the meter_status table to the meter_totals table, 
calculate the difference since midnight and add these informatins aswell.

'''

import psycopg2
import datetime
from datetime import timedelta  

from pgGetTimeStamp import pgGetTimeStamp
from pgGetMeterTotals import pgGetMeterTotals


from pgConfig import pgConfig
from pgGetMeterValues import pgGetMeterValues

#
def pgInsertTotals():
    conn = None

    # For inserts made before 00:05:00 will be set to 00:00:00 
    time_ref = datetime.time(0, 5, 0)
    time_stamp = pgGetTimeStamp()
    date = time_stamp.date()

    if time_stamp.time() < time_ref:
        time = datetime.time(0, 0, 0)
        refDate = time_stamp - timedelta(days=1)
        refDate = refDate.date()
    else:
        time = "{:%H:%M:%S}".format(time_stamp.time())
        refDate = date

    # Get last totalse

    refTime = datetime.time(0, 0, 0)
    lastTotals = pgGetMeterTotals( refDate, refTime)



    # Get surrent meter kWh'rs from meter_status ordered by meter numer
    meterValues = pgGetMeterValues()

#    updated_rows = None
    
    try:
        # read connection parameters
        params = pgConfig()

        # connect to the PostgreSQL server
        action = "pgInsertTotals - Connect to PostGres database: "
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()



        # Insert kWh'rs into meter_totals
        action = "pgInsertTotals - Insert into meter_totals: "
        if lastTotals != None:
            insert_stmt = "INSERT INTO meter_totals (date, time, meter_no_1, meter_no_2, meter_no_3, \
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
            insert_stmt = "INSERT INTO meter_totals (date, time, meter_no_1, meter_no_2, meter_no_3, \
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
#            return updated_rows
        

if __name__ == '__main__':
    
    pgInsertTotals()

    print(f'Totals updated')