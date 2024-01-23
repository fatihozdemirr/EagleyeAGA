import serial
import time
import threading
import sqlite3

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

co_value = 0.0
co2_value = 0.0
ch4_value = 0.0

span_old_1 = 0
span_old_2 = 0
span_old_3 = 0

button_id = None
button_status = False

# Lock for thread safety
lock = threading.Lock()
calibration_in_progress = False

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
########## burası
def read_sensor(sensor_id, sensor_name, register_address, quantity, ser, button_id):
    global co_value, co2_value, ch4_value, calibration_in_progress,span_old_1,span_old_2,span_old_3
    try:
        slave_id_hex = format(sensor_id, '02X')
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
            sensor_value = int.from_bytes(sensor_value_bytes, byteorder='big')
            if not calibration_in_progress:
                if sensor_id == 43:             ## sensörün manueldeki cevap karşılığı = 5 = 0.01
                    sensor_value *= 0.01
                elif sensor_id == 2:            ## sensörün manueldeki cevap karşılığı = 4 = 0.001
                    sensor_value *= 0.001
                elif sensor_id == 79:           ## sensörün manueldeki cevap karşılığı = 4 = 0.001
                    sensor_value *= 0.001

                # Sensördeki Anlık Okunan Değerler
                if sensor_id == 43:
                    co_value = "{:.2f}".format(sensor_value)
                elif sensor_id == 2:
                    co2_value = "{:.3f}".format(sensor_value)
                elif sensor_id == 79:
                    ch4_value = "{:.2f}".format(sensor_value)
            
            # 84 Adres Sorgusunda Manueldeki Formülde Bulunan Span_old Değeri
            if calibration_in_progress:
                if sensor_id == 43 and button_id == 'buttonspan_1':
                    span_old_1 = sensor_value
                    # print('co_span_value:',span_old_1)
                    update_query = "UPDATE sensor SET SpanOld = ? WHERE id = ?"
                    cursor.execute(update_query, (span_old_1, sensor_id))
                    conn.commit()
                    calibration_in_progress = False
                elif sensor_id == 2 and button_id == 'buttonspan_2':
                    span_old_2 = sensor_value
                    # print('co2_span_value:',span_old_2)
                    update_query = "UPDATE sensor SET SpanOld = ? WHERE id = ?"
                    cursor.execute(update_query, (span_old_2, sensor_id))
                    conn.commit()
                    calibration_in_progress = False
                elif sensor_id == 79 and button_id == 'buttonspan_3':
                    span_old_3 = sensor_value
                    # print('ch4_span_value:',span_old_3)
                    update_query = "UPDATE sensor SET SpanOld = ? WHERE id = ?"
                    cursor.execute(update_query, (span_old_3, sensor_id))
                    conn.commit()
                    calibration_in_progress = False
                    
        else:
            print(f"CRC kontrolü başarısız. {sensor_name} (ID: {sensor_id}) yanıtı kontrol edin.")

    except KeyboardInterrupt:
        print("Kullanıcı tarafından kesildi.")
    except Exception as e:
        print(f"Hata: {e}")

# Seri port ayarları
port = 'COM6'
baudrate = 57600
parity = serial.PARITY_EVEN
stopbits = serial.STOPBITS_ONE

# Seri port nesnesini oluştur
ser = serial.Serial(port=port, baudrate=baudrate, parity=parity, stopbits=stopbits, timeout=1)
 
 
 
 
 
 
def update_conc_cal(conc_cal):
    global concentration_cal
    concentration_cal = conc_cal
    print('Received conc_cal:', concentration_cal)
    
def calibratebuttoninformation(button_status):
    global calibratebutton
    calibratebutton = button_status
    print("button_status:",button_status)






def read_and_calibrate_sensor(sensor_id, sensor_name, button_id):
    global ser
    try:
        read_sensor(sensor_id, sensor_name, 84, 1, ser, button_id)
    except Exception as e:
        print(f"Hata: {e}")
        
# SPAN fonksiyonunu çağırarak sensör Span_old değerini okuma işlemlerini başlat
def span_calibration_queries(button_id, action):
    global calibration_in_progress
    try:
        if not calibration_in_progress:            
                
            read_and_calibrate_sensor(43, "%CO", 'buttonspan_1')
            read_and_calibrate_sensor(2, "%CO2", 'buttonspan_2')
            read_and_calibrate_sensor(79, "%CH4", 'buttonspan_3')
            
            print(f"Button {button_id} calibration in progress for action: {action}")
            calibration_in_progress = False
            
        else:
            print("Calibration not in progress.")
            
    except Exception as e:
        print(f"Hata: {e}")

    if not calibration_in_progress:
        print("Span da 84 adresinden sorgu yapıldı")
        # print(calibration_in_progress)  False olarak döndü
    else:
        print("Calibration not in progress.")
    
# Timer fonksiyonunu çağırarak sensör OKUMA işlemlerini başlat
def read_sensors():
    global co_value, co2_value, ch4_value, calibration_in_progress
    with lock:
        threading.Timer(10, read_sensors).start()  
        if calibration_in_progress:
            return
        read_sensor(43, "%CO", 10, 1, ser,'some_button_id')
        time.sleep(0.3)
        read_sensor(2, "%CO2", 10, 1, ser,'some_button_id')
        time.sleep(0.3)
        read_sensor(79, "%CH4", 10, 1, ser,'some_button_id')
        time.sleep(0.3)
        
# İlk okumayı başlat
read_sensors()



#Span_new = Conc_cal x Span_old / Conc_old
#written in the Span register (0x0054).
