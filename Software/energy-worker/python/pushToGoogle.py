'''
 This module rquires:
- postgres database is accessable, and tables have been created by the pgCeateTabels.py module. (typicaly done when energy-werker.py have been run once.)
- The environmentvariable GOOGLE_WEBHOOK_URL 

Currently the URL for the google webhook is:    http://192.168.10.102/energyRegistrations/updateEnergyRegistrations
The request will take the form:                 function=updateSheet&dataString=<Value for meter 1>,<Value for meter 2>,....<Value for meter7>

The resulting GET request will be:
GET /energyRegistrations/updateEnergyRegistrations?function=updateSheet&dataString=<Value for meter 1>,<Value for meter 2>,....<Value for meter7>

Eksample
 * http://192.168.10.102/energyRegistrations/updateEnergyRegistrations?function=updateSheet&dataString=279.97,752.04,260.03,441.21,806.67,1.08,3362.79
 '''
import os
import requests


from pgGetMeterValues import pgGetMeterValues

def pushToGoogle():

    request = """%s?function=updateSheet&dataString=""" % (os.environ['GOOGLE_WEBHOOK_URL'])
    
    meterValues = pgGetMeterValues()

    for meterValue in meterValues:
        value = float(meterValue[0])
        request += str(value) + ","

    request = request[:-1]
    returnValue = requests.get(request)
    return returnValue

if __name__ == '__main__':
    returnValue = pushToGoogle()

    print(f'Return value from pushToGoogle: {returnValue} ')