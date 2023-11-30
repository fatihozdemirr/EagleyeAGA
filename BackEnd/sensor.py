import threading
import time
import crcmod
import serial

# Modbus CRC calculation function
crc16 = crcmod.mkCrcFun(0x18005, rev=True, initCrc=0xffff, xorOut=0x0000)

# Hex input converted to bytes array
hex_string = '01 20 00'
hex_string2 = '02 20 00'
hex_string3 = '03 20 00'

hex_array = bytes.fromhex(hex_string)
hex_array2 = bytes.fromhex(hex_string2)
hex_array3 = bytes.fromhex(hex_string3)

# Bytes array is used to create CRC byte array
hex_crc_int = crc16(hex_array)
hex_crc_bytes = hex_crc_int.to_bytes(2, byteorder='little')
hex_crc_int2 = crc16(hex_array2)
hex_crc_bytes2 = hex_crc_int2.to_bytes(2, byteorder='little')
hex_crc_int3 = crc16(hex_array3)
hex_crc_bytes3 = hex_crc_int3.to_bytes(2, byteorder='little')

# Input and CRC bytes are concatenated
port_input = hex_array + hex_crc_bytes
port_input2 = hex_array2 + hex_crc_bytes2
port_input3 = hex_array3 + hex_crc_bytes3

# Serial port is opened
ser = serial.Serial()
ser.port = "COM3"
ser.baudrate = 9600
ser.bytesize = serial.EIGHTBITS
ser.parity = serial.PARITY_EVEN
ser.stopbits = serial.STOPBITS_ONE
ser.timeout = 1
ser.open()

# Global variables for sensor values
int_value_1 = 0.0
int_value_2 = 0.0
int_value_3 = 0.0

# Lock for thread safety
lock = threading.Lock()

def readco():
    global int_value_1
    with lock:
        ser.write(port_input)
        time.sleep(0.1)
        buffer1 = ser.read(7)
        time.sleep(0.1)
        if len(buffer1) == 7:
            address = buffer1[0:1]
            if int.from_bytes(address, byteorder='little') == 1:
                value = buffer1[3:5]
                int_value_0 = int.from_bytes(value, byteorder='little')
                int_value_1 = int_value_0 / 10
                print('co:', int_value_1)

def readco2():
    global int_value_3
    with lock:
        ser.write(port_input3)
        time.sleep(0.1)
        buffer3 = ser.read(7)
        time.sleep(0.1)
        if len(buffer3) == 7:
            address = buffer3[0:1]
            if int.from_bytes(address, byteorder='little') == 3:
                value = buffer3[3:5]
                int_value_0 = int.from_bytes(value, byteorder='little')
                int_value_3 = int_value_0 / 100
                print('co2:', int_value_3)

def readch4():
    global int_value_2
    with lock:
        ser.write(port_input2)
        time.sleep(0.1)
        buffer2 = ser.read(7)
        time.sleep(0.2)
        if len(buffer2) == 7:
            address = buffer2[0:1]
            if int.from_bytes(address, byteorder='little') == 2:
                value = buffer2[3:5]
                int_value_0 = int.from_bytes(value, byteorder='little')
                int_value_2 = int_value_0 / 100
                print('ch4:', int_value_2)
                

def sensortimer():
    threading.Timer(1, sensortimer).start()
    readco()
    time.sleep(0.3)
    readco2()
    time.sleep(0.3)
    readch4()
    time.sleep(0.3)