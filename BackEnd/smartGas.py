import serial
import time
import threading

co_value = 0.0
co2_value = 0.0
ch4_value = 0.0

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

def read_sensor(sensor_id, sensor_name, register_address, quantity, ser):
    global co_value, co2_value, ch4_value
    try:
        # Decimal slave_id'yi hexadecimal formatına çevir
        slave_id_hex = format(sensor_id, '02X')

        # Modbus RTU mesajını oluşturma
        message = bytearray.fromhex(f"{slave_id_hex}03{register_address:04X}{quantity:04X}")

        # CRC hesapla
        crc_bytes = calculate_crc(message)

        # Mesajın sonuna CRC'yi ekle
        message += crc_bytes

        # Holding register okuma isteğini gönder
        ser.write(message)

        # Yanıt beklemek için kısa bir süre bekle
        time.sleep(0.1)

        # Cihazdan gelen yanıtı oku
        response = ser.read(7)  # 7 byte uzunluğunda yanıt bekleniyor

        # CRC kontrolünü yap
        if len(response) == 7 and calculate_crc(response[:-2]) == response[-2:]:
            # Yanıt doğru ise, 4. ve 5. byte'lar arasındaki değeri çıkart
            sensor_value_bytes = response[3:5]
            sensor_value = int.from_bytes(sensor_value_bytes, byteorder='big')
            if sensor_id == 43:             ##5 0.01*
                sensor_value *= 0.01
            elif sensor_id == 2:            ##4 0.001*
                sensor_value *= 0.001
            elif sensor_id == 79:           ##4 0.001*
                sensor_value *= 0.001

            # Yeni değişkenlere atama
            if sensor_id == 43:
                co_value = "{:.2f}".format(sensor_value)
                # print('co_value:',co_value)
            elif sensor_id == 2:
                co2_value = "{:.3f}".format(sensor_value)
                # print('co2_value:',co2_value)
            elif sensor_id == 79:
                ch4_value = "{:.2f}".format(sensor_value)
                # print('ch4_value:',ch4_value)
            #print(f"{sensor_name} (ID: {sensor_id}) degeri: {sensor_value}")
        else:
            print(f"CRC kontrolü başarısız. {sensor_name} (ID: {sensor_id}) yanıtı kontrol edin.")

    except KeyboardInterrupt:
        print("Kullanıcı tarafından kesildi.")
    except Exception as e:
        print(f"Hata: {e}")

# Seri port ayarları
port = 'COM3'
baudrate = 57600
parity = serial.PARITY_EVEN
stopbits = serial.STOPBITS_ONE

# Seri port nesnesini oluştur
ser = serial.Serial(port=port, baudrate=baudrate, parity=parity, stopbits=stopbits, timeout=1)

# Timer fonksiyonunu çağırarak sensör okuma işlemlerini başlat
def read_sensors():
    global co_value, co2_value, ch4_value
    with lock:
        threading.Timer(10, read_sensors).start()  
        read_sensor(43, "%CO", 10, 1, ser)
        time.sleep(0.3)
        read_sensor(2, "%CO2", 10, 1, ser)
        time.sleep(0.3)
        read_sensor(79, "%CH4", 10, 1, ser)
        time.sleep(0.3)
        
# with serial.Serial(port=port, baudrate=baudrate, parity=parity, stopbits=stopbits, timeout=1) as ser:
#     # Her sensör için okuma fonksiyonunu çağır
#         read_sensor(43, "%CO", 79, 1, ser)
#         read_sensor(2, "%CO2", 79, 1, ser)
#         read_sensor(79, "%CH4", 79, 1, ser)

# İlk okumayı başlat
read_sensors()




