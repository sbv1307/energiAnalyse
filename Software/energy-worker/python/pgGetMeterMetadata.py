import psycopg2

from pgConfig import pgConfig

def pgGetMeterMetadata(key):
    # Query Meter metadata from table meter_metadata
    conn = None

    try:
        # read connection parameters
        action = "pgGetMeterdata - Connect to PostGres database: "
        params = pgConfig()

        # connect to the PostgreSQL server
        action = "pgGetMeterdata - Connect to PostGres database: "
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()

        # Select pulse per kWh from table meter
        action = "pgGetMeterdata - Select * FROM meter_metadata"
        cur.execute("SELECT * \
                    FROM meter_metadata \
                    WHERE meter_no = {}".format(key))

        meter_metadata = cur.fetchall()[0]

        # close the communication with the PostgreSQL
        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(action, error)

    finally:
        if conn is not None:
            conn.close()

    return meter_metadata

if __name__ == '__main__':
    meter_no = 1
    while meter_no < 8:
        meter_metadata = pgGetMeterMetadata(meter_no)
        print(f'Metadata       for meter number {meter_no} is {meter_metadata} ')

        meter_name = meter_metadata[1]
        print(f'meter_name     for meter number {meter_no} is {meter_name}')

        pulse_per_kWh = meter_metadata[2]
        print(f'pulse_per_kWh  for meter number {meter_no} is {pulse_per_kWh}')
        
        max_energy = meter_metadata[3]
        print(f'max_energy     for meter number {meter_no} is {max_energy}')
        
        power_factor = meter_metadata[4]
        print(f'power_factor   for meter number {meter_no} is {power_factor}')
        
        deviation_pct = meter_metadata[5]
        print(f'deviation_pct  for meter number {meter_no} is {deviation_pct}')
    
        print("-----------------------------------------------")
        meter_no += 1
