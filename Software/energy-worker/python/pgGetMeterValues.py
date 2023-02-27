import psycopg2

from pgConfig import pgConfig

def pgGetMeterValues():
    # Query Meter status from table meter_status 
    conn = None

    try:
        action = "pgGetMeterCounts - Get configuration calling pgConfig()"
        # read connection parameters
        params = pgConfig()

        # connect to the PostgreSQL server
        action = "pgGetMeterCounts - Connect to PostGres database: "
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()

        # Get  meter counts from meter_status
        action = "pgGetMeterCounts - Select kWh FROM meter_status ... "
        cur.execute("SELECT kWh FROM meter_status ORDER BY meter_no")

        meter_values = cur.fetchall()

        # close the communication with the PostgreSQL
        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(action, error)

    finally:
        if conn is not None:
            conn.close()
    
    return meter_values



if __name__ == '__main__':
    meter_values = pgGetMeterValues()
    print(f'Row from table meter_status: {meter_values} \n')
    
    meter_no = 1
    for meter_value in meter_values:
        print(f'Meter value for meter number {meter_no} is {meter_value} ')
    
