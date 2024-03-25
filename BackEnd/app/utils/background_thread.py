from GlobalVars import globalVars
from datetime import datetime, timedelta
import time
import random

def background_thread(socketio):
    while True:
        time.sleep(globalVars.ValueUpdateInterval)       
        dtNow = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        minDate = datetime.now() - timedelta(seconds=globalVars.TimeRangeMin)
        
        #For Testing
        if(globalVars.IsDebugging):
            globalVars.CO_Result = round(random.uniform(0, 50), 2)
            globalVars.CO2_Result = round(random.uniform(0, 5), 3)
            globalVars.CH4_Result = round(random.uniform(0, 10), 2)
       
                         
        socketio.emit('chart_sensor_data', {
            'MinDate': minDate.strftime('%Y-%m-%d %H:%M:%S') ,
            'time': dtNow,
            'valueCO': globalVars.CO_Result,
            'valueCO2': globalVars.CO2_Result,
            'valueCH4': globalVars.CH4_Result,
        })
        
           