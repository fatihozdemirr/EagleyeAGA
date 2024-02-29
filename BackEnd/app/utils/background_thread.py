from GlobalVars import globalVars
from datetime import datetime
import time

def background_thread(socketio):
    while True:
        time.sleep(globalVars.ValueUpdateInterval)
        socketio.emit('chart_sensor_data', {
            'MaxPoint':globalVars.MaxPoint,
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'valueCO': globalVars.CO_Result,
            'valueCO2': globalVars.CO2_Result,
            'valueCH4': globalVars.CH4_Result,
        })