''''
USAGE:
    pgUpdateMetercount( key, value)

where
    key     is a sting and has the format: Chanel:<meter_number>:Timestamp
    value   is a string holding a integervalue which reprecent the meter counts, which will be updated for the current meter_number 
            

'''
from pgGetTimeStamp import pgGetTimeStamp
from pgGetMeterMetadata import pgGetMeterMetadata
from pgGetMeterStatus import pgGetMeterStatus
from pgUpdateMeterStatus import pgUpdateMeterStatus


import time
import psycopg2

def pgUpdateMeterCount( key, value):

    # Slpit key in order to use channel as meter_no for key
    s_key = key.split(":")
    meter_no = s_key[1]
    
    time_stamp = pgGetTimeStamp()

    # Get pulse_per_kWh from table meter_metadata 
    meter_metadata = pgGetMeterMetadata(meter_no)
    pulse_per_kWh = meter_metadata[2]

    # Get dataset from meter-status and extract data. 
    meter_status = pgGetMeterStatus(meter_no)
    upper_index = meter_status[0]
    reference_watt_consumption = meter_status[2]
    pulse_time_stamp = meter_status[5]
    pulse_period = meter_status[6]
    cor_time_stamp =  meter_status[7]

    # Convert value (sting) to integet
    kWh =  int(value) / 100
    meter_counts = int(kWh * pulse_per_kWh)
    
    # Update table meter_status    
    pgUpdateMeterStatus(upper_index, meter_no, reference_watt_consumption, meter_counts, kWh, pulse_time_stamp, pulse_period, cor_time_stamp, time_stamp)

if __name__ == '__main__':

    n = 1
    while n < 8:
        meter_no = str(n)
        key = 'Chanel:' + meter_no + ':Timestamp'
        value = "123456"
        pgUpdateMeterCount( key, value)
        n += 1
 