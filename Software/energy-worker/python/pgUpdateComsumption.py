import psycopg2

from pgConfig import pgConfig

# NOTE The function will only update selected fields!!! Fields in gray will not be updated!!!
def pgUpdateComsumption(index, meter_no, watt_consumption, meter_counts, kWh, pulse_time_stamp, pulse_period, cor_time_stamp, time_stamp):
    conn = None
    updated_rows = None
    
    try:
        # read connection parameters
        params = pgConfig()

        # connect to the PostgreSQL server
        action = "pgInsertConsumption - Connect to PostGres database: "
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()

        # Update data in table consumption
        action = "pgupdateComsumption - UPDATE consumption: "

        insert_stmt = "UPDATE consumption SET watt_consumption = %s, meter_counts = %s, kWh= %s, \
                        pulse_time_stamp = %s, pulse_period = %s, cor_time_stamp = %s, time_stamp = %s  WHERE index = %s"
        cur.execute(insert_stmt, (watt_consumption, meter_counts, kWh, pulse_time_stamp, pulse_period, cor_time_stamp, time_stamp, index))
        updated_rows = cur.rowcount

         # close the communication with the PostgreSQL
        cur.close()

        # commit the changes
        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        print(action, error)

    finally:
        if conn is not None:
            conn.close()
            return updated_rows
        

if __name__ == '__main__':
    updated_rows = None

    # read the connection parameters
    params = pgConfig()

    # connect to the PostgreSQL server
    action = "Connect to database: "

    conn = psycopg2.connect(**params)

    # create a cursor
    cur = conn.cursor()

    # Get durrent time from postgres server
    action = "Get current time: "

    cur.execute("SELECT NOW()")
    time_stamp = cur.fetchone()[0]

    # close the communication with the PostgreSQL
    cur.close()

    index = int(1)
    print(f'Row number to be updated: {type(index)} {index} ')

    meter_no = int(1)
    print(f'Meter number: {type(meter_no)} {meter_no} ')
    
    watt_consumption = int(250)
    print(f'watt consumption: {type(watt_consumption)} {watt_consumption} ')
    
    meter_counts = int(25000)
    print(f'Meter counts: {type(meter_counts)} {meter_counts} ')
    
    kWh = float(22.0)
    print(f'KWh: {type(kWh)} {kWh} ')
    
    pulse_time_stamp = int(560000)
    print(f'pulse_time_stamp: {type(pulse_time_stamp)} {pulse_time_stamp} ')

    pulse_period = int(5600)
    print(f'Puls periopde: {type[pulse_period]} {pulse_period} ')

    cor_time_stamp = "2023-02-18 06:48:25.426979"
    print(f'Time Stamp: {type(cor_time_stamp)} {cor_time_stamp} ')

    print(f'Time Stamp: {type(time_stamp)} {time_stamp} ')

    updated_rows = pgUpdateComsumption(index, meter_no, watt_consumption, meter_counts, kWh, pulse_time_stamp, pulse_period, cor_time_stamp, time_stamp)

    print(f'Number of rows updated: {updated_rows}')