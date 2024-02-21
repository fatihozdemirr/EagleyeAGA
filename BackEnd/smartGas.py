import serial
import time
import threading
from GlobalVars import globalVars

span_old_1 = 0
span_old_2 = 0
span_old_3 = 0

button_id = None
conc_cal = 0.0
calibration_in_progress = False
zero_in_progress = False

# Lock for thread safety
lock = threading.Lock()

def calculate_crc(data_bytes):
    crc = 0xFFFF

    for byte in data_bytes:
        crc ^= byte

        for _ in range(8):
            if crc & 0x0001:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1

    return crc.to_bytes(2, byteorder='little')

def read_sensor(sensor_id, sensor_name, register_address, quantity, ser, button_id, calibration_in_progress, conc_cal):
    global span_old_1,span_old_2,span_old_3
    try:
        slave_id_hex = format(sensor_id, '02X')
        register_address = 84 if calibration_in_progress else 10
        message = bytearray.fromhex(f"{slave_id_hex}03{register_address:04X}{quantity:04X}")
        crc_bytes = calculate_crc(message)
        message += crc_bytes
        ser.write(message)
        time.sleep(0.1)
        
        # 10 Adres Sorgusundaki Yeni Değerler
        response = ser.read(7)  # 7 byte uzunluğunda yanıt bekleniyor
        if len(response) == 7 and calculate_crc(response[:-2]) == response[-2:]:
            # Yanıt doğru ise, 4. ve 5. byte'lar arasındaki değeri çıkart
            sensor_value_bytes = response[3:5]
            sensor_value = int.from_bytes(sensor_value_bytes, byteorder='big', signed=True)
            
            if not calibration_in_progress:
                if sensor_id == 43:             ## sensörün manueldeki cevap karşılığı = 5 = 0.01
                    sensor_value *= 0.01
                elif sensor_id == 2:            ## sensörün manueldeki cevap karşılığı = 4 = 0.001
                    sensor_value *= 0.001
                elif sensor_id == 79:           ## sensörün manueldeki cevap karşılığı = 4 = 0.001
                    sensor_value *= 0.001

                # Sensördeki Anlık Okunan Değerler
                if sensor_id == 43:
                    globalVars.CO_Read = float("{:.2f}".format(sensor_value))
                    globalVars.CO_Result = globalVars.CO_Read + globalVars.CO_Offset
                elif sensor_id == 2:
                    globalVars.CO2_Read = float("{:.3f}".format(sensor_value))
                    globalVars.CO2_Result = globalVars.CO2_Read + globalVars.CO2_Offset
                elif sensor_id == 79:
                    globalVars.CH4_Read = float("{:.2f}".format(sensor_value))
                    globalVars.CH4_Result = globalVars.CH4_Read + globalVars.CH4_Offset
                    
            # 84 Adres Sorgu Başlangıcı
            else:
                if sensor_id == 43 and button_id == 'CObuttonspan':
                    span_old_1 = sensor_value
                    Span_new_CO = int(conc_cal * span_old_1 / globalVars.CO_Read)
                    write_to_sensor(sensor_id, register_address, ser, Span_new_CO)
                elif sensor_id == 2 and button_id == 'CO2buttonspan':
                    span_old_2 = sensor_value
                    Span_new_CO2 = int(conc_cal * span_old_2 / globalVars.CO2_Read)
                    write_to_sensor(sensor_id, register_address, ser, Span_new_CO2)
                elif sensor_id == 79 and button_id == 'CH4buttonspan':
                    span_old_3 = sensor_value
                    Span_new_CH4 = int(conc_cal * span_old_3 / globalVars.CH4_Result)
                    write_to_sensor(sensor_id, register_address, ser, Span_new_CH4)

    except KeyboardInterrupt:
        print("Kullanıcı tarafından kesildi.")
    except Exception as e:
        print("Hatastr:", str(e))

def write_to_sensor(sensor_id, register_address, ser, value_to_write):
    try:
        slave_id_hex = format(sensor_id, '02X')
        message = bytearray.fromhex(f"{slave_id_hex}06{register_address:04X}{value_to_write:04X}")
        crc_bytes = calculate_crc(message)
        message += crc_bytes
        ser.write(message)
        time.sleep(0.1)
                
        response = ser.read(8) 
        if len(response) == 8 and calculate_crc(response[:-2]) == response[-2:]:
            print("Yazma başarılı!")
        else:
            print("Yazma başarısız!")

    except Exception as e:
        print(f"Error writing to sensor: {e}")
        
# SERIAL PORT SETTING
port = 'COM6'
baudrate = 57600
parity = serial.PARITY_EVEN
stopbits = serial.STOPBITS_ONE

# CREATE SERIAL PORT OBJECT
ser = serial.Serial(port=port, baudrate=baudrate, parity=parity, stopbits=stopbits, timeout=1)
   
def read_and_span_calibrate_sensor(sensor_id, sensor_name, button_id, calibration_in_progress, conc_cal):
    global ser
    try:
        read_sensor(sensor_id, sensor_name, 84, 1, ser, button_id, calibration_in_progress, conc_cal)
    except Exception as e:
        print(f"Hata: {e}")
        
# SPAN CALIBRATE
def span_calibration_queries(button_id, calibrationState, conc_cal):
    calibration_in_progress = calibrationState
    try:
        if button_id in ['CObuttonspan', 'CO2buttonspan', 'CH4buttonspan']:
            if calibration_in_progress:        
                if button_id == 'CObuttonspan':
                    read_and_span_calibrate_sensor(43, "%CO", button_id, calibration_in_progress, conc_cal)
                elif button_id == 'CO2buttonspan':
                    read_and_span_calibrate_sensor(2, "%CO2", button_id, calibration_in_progress, conc_cal)
                elif button_id == 'CH4buttonspan':
                    read_and_span_calibrate_sensor(79, "%CH4", button_id, calibration_in_progress, conc_cal)
                else:
                    print("Invalid button_id. Calibration not in progress.")
            else:
                print("Span calibration not in progress.")
            
    except Exception as e:
        print(f"Hata: {e}")
        
    finally:
        calibration_in_progress = False
        print(f"calibration_in_progress_finally: {calibration_in_progress}")
        
# ZERO CALIBRATE
def zero_calibration_queries(zero_in_progress):
    try:
        if zero_in_progress:    
            write_to_sensor(43, 71, ser, 1)
            write_to_sensor(2,  71, ser, 1)
            write_to_sensor(79, 71, ser, 1)
        else:
            print("Zero calibration not in progress.")
            
    except Exception as e:
        print(f"Hata: {e}")
        
    finally:
        zero_in_progress = False
        print(f"zero_calibration_in_progress_finally: {zero_in_progress}")

# ACTUAL READING
def read_sensors():
    with lock:
        threading.Timer(1, read_sensors).start()  
        if not calibration_in_progress or not zero_in_progress:
            read_sensor(43, "%CO", 10, 1, ser,'some_button_id',calibration_in_progress,conc_cal)
            read_sensor(2, "%CO2", 10, 1, ser,'some_button_id',calibration_in_progress,conc_cal)
            read_sensor(79, "%CH4", 10, 1, ser,'some_button_id',calibration_in_progress,conc_cal)
        else:
            print("Kalibrasyon işlemi başladı.")
 
# Current values ​​are sent via SocketIO.
def update_ui(socketio):
    while True:
        socketio.emit('sensor_data', {'co_offset': globalVars.CO_Offset, 
                                      'co2_offset': globalVars.CO2_Offset, 
                                      'ch4_offset': globalVars.CH4_Offset,
                                      
                                      'co_read': globalVars.CO_Read, 
                                      'co2_read': globalVars.CO2_Read, 
                                      'ch4_read': globalVars.CH4_Read,
                                      
                                      'co_result':globalVars.CO_Read + globalVars.CO_Offset,
                                      'co2_result':globalVars.CO2_Read + globalVars.CO2_Offset,
                                      'ch4_result':globalVars.CH4_Read + globalVars.CH4_Offset,
                                      
                                      'Temperature':globalVars.temp,
                                      'CH4_Factor':globalVars.ch4factor,
                                      'Alloy_Factor':globalVars.alloyfactor,
                                      'H2':globalVars.h2,
                                      })

        socketio.sleep(0.5)

