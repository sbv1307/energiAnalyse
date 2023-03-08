import psycopg2
import datetime

from pgConfig import pgConfig

def pgGetMeterTotals(date, time):
    # Query Meter status from table meter_status 
    conn = None

    try:
        action = "pgGetLastMeterTotals - Get configuration calling pgConfig()"
        # read connection parameters
        params = pgConfig()

        # connect to the PostgreSQL server
        action = "pgGetLastMeterTotals - Connect to PostGres database: "
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()

        # Get  meter counts from meter_status
        action = "pgGetLastMeterTotals - Select kWh FROM meter_status ... "
        selectStmt = "SELECT meter_no_1, meter_no_2, meter_no_3, \
                        meter_no_4, meter_no_5, meter_no_6, meter_no_7 \
                        FROM meter_totals \
                        WHERE date = '{}' and time = '{}'".format(date,time)
        cur.execute(selectStmt)

        meter_totals = cur.fetchone()

        # close the communication with the PostgreSQL
        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(action, error)

    finally:
        if conn is not None:
            conn.close()
    
    return meter_totals



if __name__ == '__main__':
    date = datetime.date(2023, 3, 8)
    time = datetime.time(0, 0, 0)

    meter_totals = pgGetMeterTotals(date, time)
    if meter_totals != None:
        print(f'Row from table meter_status: {type(meter_totals)} {meter_totals} \n')
        print(f'Row from table meter_status: {type(meter_totals[0])} {meter_totals[0]} ')
        print(f'Row from table meter_status: {type(meter_totals[1])} {meter_totals[1]} ')
        print(f'Row from table meter_status: {type(meter_totals[2])} {meter_totals[2]} ')
        print(f'Row from table meter_status: {type(meter_totals[3])} {meter_totals[3]} ')
        print(f'Row from table meter_status: {type(meter_totals[4])} {meter_totals[4]} ')
        print(f'Row from table meter_status: {type(meter_totals[5])} {meter_totals[5]} ')
        print(f'Row from table meter_status: {type(meter_totals[6])} {meter_totals[6]} ')
