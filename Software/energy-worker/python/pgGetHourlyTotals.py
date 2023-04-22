import psycopg2
import datetime

from pgConfig import pgConfig

def pgGetHourlyTotals(date, time):
    # Query Meter status from table  hourly_totals
    conn = None

    try:
        action = "pgGetLastHourlyTotals - Get configuration calling pgConfig()"
        # read connection parameters
        params = pgConfig()

        # connect to the PostgreSQL server
        action = "pgGetLastHourlyTotals - Connect to PostGres database: "
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()

        # Get  meter counts from hourly_totals
        action = "pgGetLastHourlyTotals - Select kWh FROM hourly_totals ... "
        selectStmt = "SELECT meter_no_1, meter_no_2, meter_no_3, \
                        meter_no_4, meter_no_5, meter_no_6, meter_no_7 \
                        FROM hourly_totals \
                        WHERE date = '{}' and time = '{}'".format(date,time)
        cur.execute(selectStmt)

        hourly_totals = cur.fetchone()

        # close the communication with the PostgreSQL
        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(action, error)

    finally:
        if conn is not None:
            conn.close()
    
    return hourly_totals



if __name__ == '__main__':
    date = datetime.date(2023, 3, 8)
    time = datetime.time(0, 0, 0)

    hourly_totals = pgGetMeterTotals(date, time)
    if hourly_totals != None:
        print(f'Row from table hourly_totals: {type(hourly_totals)} {hourly_totals} \n')
        print(f'Row from table hourly_totals: {type(hourly_totals[0])} {hourly_totals[0]} ')
        print(f'Row from table hourly_totals: {type(hourly_totals[1])} {hourly_totals[1]} ')
        print(f'Row from table hourly_totals: {type(hourly_totals[2])} {hourly_totals[2]} ')
        print(f'Row from table hourly_totals: {type(hourly_totals[3])} {hourly_totals[3]} ')
        print(f'Row from table hourly_totals: {type(hourly_totals[4])} {hourly_totals[4]} ')
        print(f'Row from table hourly_totals: {type(hourly_totals[5])} {hourly_totals[5]} ')
        print(f'Row from table hourly_totals: {type(hourly_totals[6])} {hourly_totals[6]} ')
