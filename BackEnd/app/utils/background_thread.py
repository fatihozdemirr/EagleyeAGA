from GlobalVars import globalVars
from datetime import datetime
import time
import random

def background_thread(socketio):
    while True:
        time.sleep(globalVars.ValueUpdateInterval)
        if(not globalVars.IsDebugging):
            socketio.emit('chart_sensor_data', {
                'MaxPoint':globalVars.MaxPoint,
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'valueCO': globalVars.CO_Result,
                'valueCO2': globalVars.CO2_Result,
                'valueCH4': globalVars.CH4_Result,
            })
        else :
            socketio.emit('chart_sensor_data', {
                'MaxPoint':globalVars.MaxPoint,
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'valueCO': round(random.uniform(0, 50), 2),
                'valueCO2': round(random.uniform(0, 5), 3),
                'valueCH4': round(random.uniform(0, 10), 2)
            })