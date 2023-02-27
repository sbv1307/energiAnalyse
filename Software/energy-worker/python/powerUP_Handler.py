#!/usr/bin/python

from pgGetMeterStatus import pgGetMeterStatus
from pgUpdateMeterStatus import pgUpdateMeterStatus
from pgGetTimeStamp import pgGetTimeStamp
from pgGetNumberOfRows import pgGetNumberOfRows


def powerUP_Handler():

    # Get number of rows in table meter-status
    number_of_rows = pgGetNumberOfRows("meter_status")

    meter_no = 1
    while meter_no <= number_of_rows:

        # Get dataset from meter-status
        meter_status = pgGetMeterStatus(meter_no)
        # upper_index sættes til nul for at pulseTimeStampHandler kan tilføje dataset til tabeellen consumption
        upper_index = meter_status[0]
        
        meter_counts = meter_status[3]
        kWh = meter_status[4]
        
        reference_watt_consumption = int(0)
        pulse_time_stamp = int(0)
        # NOTE Ved initiering og poserUP sættes den registrerede pulse_period til -1 for at vise at forringe pulse_time_stamp er ukendt.
        pulse_period = int(-1)

        time_stamp = pgGetTimeStamp()
        cor_time_stamp = time_stamp

        # Update table meter_status    
        pgUpdateMeterStatus(upper_index, meter_no, reference_watt_consumption, meter_counts, kWh, pulse_time_stamp, pulse_period, cor_time_stamp, time_stamp)
    
        meter_no += 1

if __name__ == '__main__':
    powerUP_Handler()

    print(f'Meter status updated after power up.')




