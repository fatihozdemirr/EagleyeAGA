from GlobalVars import globalVars
import time

def background_thread(socketio):
    while True:
        time.sleep(1)
        socketio.emit('chart_sensor_data', {
            'time': time.strftime('%H:%M:%S'),
            'valueCO': globalVars.CO_Read + globalVars.CO_Offset,
            'valueCO2': globalVars.CO2_Read + globalVars.CO2_Offset,
            'valueCH4': globalVars.CH4_Read + globalVars.CH4_Offset,
        })