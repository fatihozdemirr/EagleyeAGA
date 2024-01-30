import serial
import time
import threading
import sqlite3
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import app
from GlobalVars import globalVars

span_old_1 = 0
span_old_2 = 0
span_old_3 = 0

button_id = None
button_status = False
concentration_cal = 0.0

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Reel Bilgisayar/python/EagleyeAGA/BackEnd/users.db'
db = SQLAlchemy(app)

class sensor_reading_datatable(db.Model):
    __tablename__ = 'sensor_reading_value'
    id = db.Column(db.Integer, primary_key=True)
    CO = db.Column(db.Float, nullable=False)
    CO2 = db.Column(db.Float, nullable=False)
    CH4 = db.Column(db.Float, nullable=False)
    
class sensor_spanold_datatable(db.Model):
    __tablename__ = 'sensor_spanold'
    id = db.Column(db.Integer, primary_key=True)
    span_old_1 = db.Column(db.Float, nullable=False)
    span_old_2 = db.Column(db.Float, nullable=False)
    span_old_3 = db.Column(db.Float, nullable=False)

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
    global calibration_in_progress,span_old_1,span_old_2,span_old_3
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
                    globalVars.CO_Read = "{:.2f}".format(sensor_value) 
                    print('co_value:',globalVars.CO_Read )
                elif sensor_id == 2:
                    globalVars.CO2_Read = "{:.3f}".format(sensor_value)
                elif sensor_id == 79:
                    globalVars.CH4_Read = "{:.2f}".format(sensor_value)
                    
                # # Veritabanına güncelleme işlemini gerçekleştir
                # with app.app_context():
                #     sensor_reading = sensor_reading_datatable.query.filter_by(id=1).first()
                #     if sensor_reading:
                #         sensor_reading.CO = float(co_value)
                #         sensor_reading.CO2 = float(co2_value)
                #         sensor_reading.CH4 = float(ch4_value)
                #     else:
                #         sensor_reading = sensor_reading_datatable(id=1, CO=float(co_value), CO2=float(co2_value), CH4=float(ch4_value))
                #         db.session.add(sensor_reading)

                #     # Değişiklikleri veritabanına uygula
                #     db.session.commit()
                    
            # 84 Adres Sorgusunda Manueldeki Formülde Bulunan Span_old Değeri
            if calibration_in_progress:
                if sensor_id == 43 and button_id == 'buttonspan_1':
                    span_old_1 = sensor_value
                    print('spanold1:',span_old_1)
                    update_calibration_data('span_old_1', span_old_1)
                elif sensor_id == 2 and button_id == 'buttonspan_2':
                    span_old_2 = sensor_value
                    print('spanold2:',span_old_2)
                    update_calibration_data('span_old_2', span_old_2)
                elif sensor_id == 79 and button_id == 'buttonspan_3':
                    span_old_3 = sensor_value
                    print('spanold3:',span_old_3)
                    update_calibration_data('span_old_3', span_old_3)
                calibration_in_progress = False
                print("button_id3:",button_id)
                print(f"calibration_in_progressüst: {calibration_in_progress}")
        else:
            # # Veritabanına güncelleme işlemini gerçekleştir
            # with app.app_context():
            #     sensor_reading = sensor_reading_datatable.query.filter_by(id=1).first()
            #     if sensor_reading:
            #         sensor_reading.CO = 0.00
            #         sensor_reading.CO2 = 0.000
            #         sensor_reading.CH4 = 0.00
            #         print('else sensor_reading ok')
            #     else:
            #         sensor_reading = sensor_reading_datatable(id=1, CO=float(co_value), CO2=float(co2_value), CH4=float(ch4_value))
            #         db.session.add(sensor_reading)

            #     # Değişiklikleri veritabanına uygula
            #     db.session.commit()
            print(f"CRC kontrolü başarısız. {sensor_name} (ID: {sensor_id}) yanıtı kontrol edin.")

    except KeyboardInterrupt:
        print("Kullanıcı tarafından kesildi.")
    except Exception as e:
        print("Hatastr:", str(e))
        print("Hata:", (e))
        # Hata durumunda geri al (rollback)
        db.session.rollback()

def update_calibration_data(column_name, value):
    # Veritabanına güncelleme işlemini gerçekleştir
    with app.app_context():
        calibration_data = sensor_spanold_datatable.query.first()
        if calibration_data:
            if column_name == 'span_old_1':
                calibration_data.span_old_1 = float(value)
            elif column_name == 'span_old_2':
                calibration_data.span_old_2 = float(value)
            elif column_name == 'span_old_3':
                calibration_data.span_old_3 = float(value)
        else:
            calibration_data = sensor_spanold_datatable(span_old_1=float(span_old_1), span_old_2=float(span_old_2), span_old_3=float(span_old_3))
            db.session.add(calibration_data)

        # Değişiklikleri veritabanına uygula
        db.session.commit()
        
# Seri port ayarları
port = 'COM3'
baudrate = 57600
parity = serial.PARITY_EVEN
stopbits = serial.STOPBITS_ONE

# Seri port nesnesini oluştur
ser = serial.Serial(port=port, baudrate=baudrate, parity=parity, stopbits=stopbits, timeout=1)
 
 
def update_conc_cal(conc_cal):
    global concentration_cal
    concentration_cal = conc_cal
    
def calibratebuttoninformation(button_status):
    global calibratebutton,concentration_cal
    calibratebutton = button_status
    # print("button_status:",calibratebutton)
    # print("concentration_cal in calibratebuttoninformation:", concentration_cal)
    # print("button_id in calibratebuttoninformation:", button_id) ### button_id değerini bu fonksiyonda kullanılacak
    

def read_and_calibrate_sensor(sensor_id, sensor_name, button_id):
    global ser
    try:
        read_sensor(sensor_id, sensor_name, 84, 1, ser, button_id)
        print("button_id2:",button_id)
    except Exception as e:
        print(f"Hata: {e}")
        
# SPAN fonksiyonunu çağırarak sensör Span_old değerini okuma işlemlerini başlat
def span_calibration_queries(button_id, action):
    global calibration_in_progress
    print("button_id1:",button_id)
    try:
        if button_id in ['buttonspan_1', 'buttonspan_2', 'buttonspan_3']:
            calibration_in_progress = True
            if calibration_in_progress:            
                if button_id == 'buttonspan_1':
                    read_and_calibrate_sensor(43, "%CO", button_id)
                elif button_id == 'buttonspan_2':
                    read_and_calibrate_sensor(2, "%CO2", button_id)
                elif button_id == 'buttonspan_3':
                    read_and_calibrate_sensor(79, "%CH4", button_id)
                else:
                    print("Invalid button_id. Calibration not in progress.")
            else:
                print("Calibration not in progress.")
            
    except Exception as e:
        print(f"Hata: {e}")
        
    finally:
        print("Span da 84 adresinden sorgu yapıldı, spanold değeri sorgulandı.")
        calibration_in_progress = False
        print(f"calibration_in_progressalt: {calibration_in_progress}")
    
# Timer fonksiyonunu çağırarak sensör OKUMA işlemlerini başlat
def read_sensors():
    global co_value, co2_value, ch4_value, calibration_in_progress
    with lock:
        threading.Timer(1, read_sensors).start()  
        if not calibration_in_progress:
            read_sensor(43, "%CO", 10, 1, ser,'some_button_id')
            # time.sleep(0.3)
            read_sensor(2, "%CO2", 10, 1, ser,'some_button_id')
            # time.sleep(0.3)
            read_sensor(79, "%CH4", 10, 1, ser,'some_button_id')
            # time.sleep(0.3)
            print("Sensör okumaları devam ediyor.")

        else:
            print("Kalibrasyon işlemi başladı.")
        
# İlk okumayı başlat
# read_sensors()

#Span_new = Conc_cal x Span_old / Conc_old
#written in the Span register (0x0054).
