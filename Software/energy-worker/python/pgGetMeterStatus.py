import psycopg2

from pgConfig import pgConfig

def pgGetMeterStatus(key):
    # Query Meter status from table meter_status
    conn = None

    try:
        # read connection parameters
        params = pgConfig()

        # connect to the PostgreSQL server
        action = "pgGetMeterStatus - Connect to PostGres database: "
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()

        # Get  meter counts from meter_status
        action = "pgGetMeterStatus - Select * FROM meter_status: "
        cur.execute("SELECT * \
                FROM meter_status \
                WHERE meter_no = {}".format(key))   

        meter_status = cur.fetchall()[0]

        # close the communication with the PostgreSQL
        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(action, error)

    finally:
        if conn is not None:
            conn.close()
    
    return meter_status



if __name__ == '__main__':
    meter_status = pgGetMeterStatus("1")
    print(f'Row from table meter_status: {meter_status} \n')
    
    upper_index = meter_status[0]
    print(f'Meter Upper_index:          {type(upper_index)} {upper_index} ')
    
    meter_no = meter_status[1]
    print(f'Meter number:               {type(meter_no)} {meter_no} ')

    reference_watt_consumption = meter_status[2]
    print(f'reference_watt_consumption: {type(reference_watt_consumption)} {reference_watt_consumption} ')
    
    meter_counts = meter_status[3]
    print(f'Meter counts:               {type(meter_counts)} {meter_counts} ')

    kWh = meter_status[4]
    print(f'KWh:                        {type(kWh)} {kWh} ')
    
    pulse_time_stamp = meter_status[5]
    print(f'pulse_time_stamp:           {type(pulse_time_stamp)} {pulse_time_stamp} ')
    
    pulse_period = meter_status[6]
    print(f'Puls periode:               {type(pulse_period)} {pulse_period} ')
    
    cor_time_stamp =  meter_status[7]
    print(f'Korrigeret time stamp:      {type(cor_time_stamp)} {cor_time_stamp} ')

    timeStamp = meter_status[7]
    print(f'Time Stamp:                 {type(timeStamp)} {timeStamp} ')
 