import psycopg2

from pgConfig import pgConfig

def pgInsertConsumption(meter_no, watt_consumption, meter_counts, kWh, pulse_time_stamp, pulse_period, cor_time_stamp, time_stamp):
    conn = None
    index = None

    try:
        # read connection parameters
        params = pgConfig()

        # connect to the PostgreSQL server
        action = "pgInsertConsumption - Connect to PostGres database: "
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()

        # Insert data into consumption
        action = "pgInsertConsumption - INSERT INTO consumption: "
        insert_stmt = "INSERT INTO consumption (meter_no,\
            watt_consumption, meter_counts, kWh, pulse_time_stamp, pulse_period, cor_time_stamp, time_stamp) \
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)RETURNING index"
        cur.execute(insert_stmt, (meter_no, watt_consumption, meter_counts, kWh, pulse_time_stamp, pulse_period, cor_time_stamp, time_stamp))
        index = cur.fetchone()[0]

         # close the communication with the PostgreSQL
        cur.close()

        # commit the changes
        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        print(action, error)

    finally:
        if conn is not None:
            conn.close()
            return index
        

if __name__ == '__main__':
    index = None

    meter_no = int(1)
    print(f'Meter number: {type(meter_no)} {meter_no} ')
    
    watt_consumption = int(125)
    print(f'watt consumption: {type(watt_consumption)} {watt_consumption} ')
    
    meter_counts = int(2200)
    print(f'Meter counts: {type(meter_counts)} {meter_counts} ')
    
    kWh = float(2.2)
    print(f'KWh: {type(kWh)} {kWh} ')
    
    pulse_time_stamp = int(360000)
    print(f'pulse_time_stamp: {type(pulse_time_stamp)} {pulse_time_stamp} ')

    pulse_period = int(3600)
    print(f'Puls periopde: {type[pulse_period]} {pulse_period} ')

    cor_time_stamp = "2023-01-17 06:48:25.426979"
    print(f'Time Stamp: {type(cor_time_stamp)} {cor_time_stamp} ')

    time_stamp = "2023-01-17 06:48:25.426979"
    print(f'Time Stamp: {type(time_stamp)} {time_stamp} ')
    
    index = pgInsertConsumption(meter_no, watt_consumption, meter_counts, kWh, pulse_time_stamp, pulse_period, cor_time_stamp, time_stamp)

    print(f'Index of inserted item is: {index}')
