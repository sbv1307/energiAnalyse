'''

'''
import psycopg2

from pgConfig import pgConfig

def pgUpdateMeterStatus(upper_index, key, reference_watt_consumption, meter_counts, kWh, pulse_time_stamp, pulse_period, cor_time_stamp, time_stamp):
    # Query time stamp 
    conn = None

    try:
        # read connection parameters
        params = pgConfig()

        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()

        cur.execute("UPDATE meter_status \
                    SET upper_index = {}, \
                        reference_watt_consumption  = {}, \
                        meter_counts = {}, \
                        kWh = {}, \
                        pulse_time_stamp = {}, \
                        pulse_period = {}, \
                        cor_time_stamp = '{}', \
                        time_stamp = '{}' \
                    WHERE  meter_no = {}".format(upper_index, reference_watt_consumption, \
                        meter_counts, kWh, pulse_time_stamp, pulse_period, \
                        cor_time_stamp, time_stamp, key ) )

        # close the communication with the PostgreSQL
        cur.close()

        # commit the changes
        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    finally:
        if conn is not None:
            conn.close()

if __name__ == '__main__':
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

    index = 1
    meter_no = 1
    watt_consumption = int(1)
    meter_counts = int(1)
    kWh = float(1.0)
    pulse_time_stamp = int(1)
    pulse_period = int(1)
    cor_time_stamp = time_stamp


    pgUpdateMeterStatus(index, meter_no, watt_consumption, meter_counts, kWh, pulse_time_stamp, pulse_period, cor_time_stamp, time_stamp)
    
    print(f'Meter status updated for meter number: {meter_no}')