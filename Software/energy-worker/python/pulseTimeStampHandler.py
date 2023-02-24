'''
USAGE:
    pulseTimeStampHandler ( key, value)

where
    key     is a sting and has the format: Chanel:<meter_number>:Timestamp
    value   is a string holding a integervalue which reprecent a time stamp in millisecunds 
            As is origion is fra Arduino, the value is expected to be 0 until 2^32 (incl.)

'''

import time
import psycopg2

# import sleet during developent (Used when module runs as main)
from time import sleep
from powerUP_Handler import powerUP_Handler


from pgGetTimeStamp import pgGetTimeStamp
from pgGetMeterMetadata import pgGetMeterMetadata
from pgGetMeterStatus import pgGetMeterStatus
from pgInsertConsumption import pgInsertConsumption
from pgUpdateMeterStatus import pgUpdateMeterStatus
from pgUpdateComsumption import pgUpdateComsumption


def pulseTimeStampHandler( key, value):

    # Slpit key in order to use channel as meter_no for key
    s_key = key.split(":")
    meter_no = s_key[1]
    
    # Convert value (sting) to integet
    pulse_time_stamp = int(value)

    time_stamp = pgGetTimeStamp()

    # Get meter metadata from table meter_metadata and extract data
    meter_metadata = pgGetMeterMetadata(meter_no)
    pulse_per_kWh = meter_metadata[2]
    max_watt_consumption = meter_metadata[3]
    deviation_pct = meter_metadata[5]

    # Get dataset from meter-status and extract data. Note: pulse_time_stamp till be extraced as previous_pulse_time_stamp
    meter_status = pgGetMeterStatus(meter_no)
    upper_index = meter_status[0]
    reference_watt_consumption = meter_status[2]
    meter_counts = meter_status[3]
    previous_pulse_time_stamp = meter_status[5]
    pulse_period = meter_status[6]
    cor_time_stamp =  meter_status[7]

    # Increase meter_counts by one
    meter_counts += int(1)

    # convert number of pulses counted (meter_counts) to kilo Watt hours (kWh)
    kWh = meter_counts / pulse_per_kWh

    # Hvis pulse_period fra tabellen meter-status >= 0 kan pulse_period udregnes og dermed watt_consumption
    # Ved Power Up (og initiering ved første opstart) sættes meter_status -> pulse_period = -1, for at vise at forringe pulse_time_stamp er ukendt.
    # Udregning af pulse_period giver ikke mening når den er baseret på et ukendt previous time_stamp.

    if pulse_period >= 0:

        # udregn pulse_periode, watt_consumption og gem datasæt
        previous_pulse_period = pulse_period

        if pulse_time_stamp < previous_pulse_time_stamp:
            pulse_time_offset = (2 ** 32) - previous_pulse_time_stamp
        else:
            pulse_time_offset = 0

        # Calculate pulse_period. The time in milliseconds since last pulse
        pulse_period = pulse_time_stamp + pulse_time_offset - previous_pulse_time_stamp

        # Hvis pulse_period, mod forventning er nigativ opdatgeres kun tabellen meter_status. Dog sættes pulse_period til
        if pulse_period > 0:
            # Calculate consumption in watt, based on estimated munber of pulses per hour from the number of millisecunds since last registration
            # The formular:
            # milisecundsPerHour = 'number of minuts per hour'(60) * 'number of secunds per minute'(60) * 'number of milisecunds per secund'(1000)
            # 'Estimated number of pulses per hour' = milisecundsPerHour / pulse_period
            # Converting to consumption in watt = 'Estimated number of pulses per hour' / 'the energy meters number of pulses per kWh' * 
            # 1000 ' to express consumption in watt and not kW
            milisecundsPerHour = 60*60*1000
            watt_consumption = int((milisecundsPerHour / pulse_period) / pulse_per_kWh * 1000)

            # Hvis den udregnede watt_consumption overstiget max værdien for metret opdatgeres kun tabellen meter_status
            if  watt_consumption < max_watt_consumption and \
                abs(reference_watt_consumption - watt_consumption) > reference_watt_consumption / 100 * deviation_pct:

                pgInsertConsumption(meter_no, watt_consumption, meter_counts, kWh, pulse_time_stamp, pulse_period, cor_time_stamp, time_stamp)
                upper_index = 0
                reference_watt_consumption = watt_consumption
            else:
                if upper_index == 0:
                    upper_index = pgInsertConsumption(meter_no, watt_consumption, meter_counts, kWh, pulse_time_stamp, pulse_period, cor_time_stamp, time_stamp)
                else:
                    pgUpdateComsumption(upper_index, meter_no, watt_consumption, meter_counts, kWh, pulse_time_stamp, pulse_period, cor_time_stamp, time_stamp)
        else:
            pulse_period = previous_pulse_period 

    else:
        pulse_period = 0

    # Update table meter_status    
    pgUpdateMeterStatus(upper_index, meter_no, reference_watt_consumption, meter_counts, kWh, pulse_time_stamp, pulse_period, cor_time_stamp, time_stamp)

if __name__ == '__main__':

    powerUP_Handler()

    meter_no = input("Indtast meter nummer (1-7)")

    key = 'Chanel:' + meter_no + ':Timestamp'
    print(f'Key: {key}')


    millis = 0
    periods = 3600,
    pause = 0
    afvigelse = 100



    for period in periods:
        entries = 0
        while entries < 10:
#            print(f'Sleeping {pause} secunds.')
#            sleep(pause)
#            pause = period / 1000
            entries += 1
            millis += period
            period -= afvigelse
            value = str(millis)
            print(f'period: {period}. Value:  {type(value)} {value} ')
            
            pulseTimeStampHandler( key, value)

#            enter = input("Hit Return to continue!")

