import os
import sqlite3
from datetime import datetime

class GlobalVars :
    def __init__(self) :
        #Working On PC
        self.DatabasePath = os.path.join(os.getcwd(), "BackEnd","users.db")
        # Working On RPI
        #self.DatabasePath  = "/home/pi/EagleyeAGA/BackEnd/users.db"        
         
        self.CO_Read = 00.00
        self.CO2_Read = 0.000
        self.CH4_Read = 00.00
        
        self.CO_Offset = 00.00
        self.CO2_Offset = 00.00
        self.CH4_Offset = 00.00
        
        self.CO_Result = 00.00
        self.CO2_Result = 00.00
        self.CH4_Result = 00.00
        
        self.temp = 0.0
        self.ch4factor = 0.0
        self.alloyfactor = 0.0
        self.h2 = 0.0
        
        self.CO_Referance = 0
        self.CO2_Referance = 0
        self.CH4_Referance = 0
        
        self.DefaultRecording = 0
        self.StartedDate = ""      
        self.RecordInterval = 1
        self.ValueUpdateInterval = 1
        self.MaxPoint = 5000
        
        self.OperationWorking = 0
        self.Port = 'COM3' if os.name == 'nt' else '/dev/ttyUSB0'
        self.load_offsets()
        self.load_live_constant()
        self.referance_reset_values()
        self.get_app_parameters()
        self.sync_recording()
         
    #Get Offset From DB
    def load_offsets(self):
        # Veritabanı bağlantısını aç
        conn = sqlite3.connect(self.DatabasePath)
        cursor = conn.cursor()

        # OFFSET değerlerini sorgula
        cursor.execute("SELECT GAS, OFFSET FROM calibration")
        rows = cursor.fetchall()

        # OFFSET değerlerini sınıf özelliklerine ata
        for gas, offset in rows:
            if gas == '%CO':
                self.CO_Offset = offset
            elif gas == '%CO2':
                self.CO2_Offset = offset
            elif gas == '%CH4':
                self.CH4_Offset = offset

        # Veritabanı bağlantısını kapat
        conn.close()
        
    def load_live_constant(self):
        # veritabanı bağlantısını aç
        conn = sqlite3.connect(self.DatabasePath)
        cursor = conn.cursor()

        # offset değerlerini sorgula
        cursor.execute("SELECT Temperature, CH4Factor,AlloyFactor,H2 from livetabledatas")
        rows = cursor.fetchall()

        # offset değerlerini sınıf özelliklerine ata
        for Temperature, CH4Factor, AlloyFactor, H2 in rows:
            self.temp = Temperature
            self.ch4factor = CH4Factor
            self.alloyfactor = AlloyFactor
            self.h2 = H2

        # veritabanı bağlantısını kapat
        conn.close()
        
    def referance_reset_values(self):
        # veritabanı bağlantısını aç
        conn = sqlite3.connect(self.DatabasePath)
        cursor = conn.cursor()

        # değerleri sorgula
        cursor.execute("SELECT COReferance, CO2Referance,CH4Referance from sensorreferance")
        rows = cursor.fetchall()

        # değerleri sınıf özelliklerine ata
        for COReferance, CO2Referance, CH4Referance in rows:
            self.CO_Referance = COReferance
            self.CO2_Referance = CO2Referance
            self.CH4_Referance = CH4Referance

        # veritabanı bağlantısını kapat
        conn.close()
        
        
    def get_app_parameters(self):
        # veritabanı bağlantısını aç
        conn = sqlite3.connect(self.DatabasePath)
        cursor = conn.cursor()

        # değerleri sorgula
        cursor.execute("SELECT * from app_parameters")
        rows = cursor.fetchall()

        # değerleri sınıf özelliklerine ata
        for row in rows:
            if row[1] == "DefaultRecording":
                self.DefaultRecording = int(row[2])
            if row[1] == "StartedDate":
                self.StartedDate = row[2]
            if row[1] == "RecordInterval":
                self.RecordInterval = int(row[2])
            if row[1] == "ValueUpdateInterval":
                self.ValueUpdateInterval = int(row[2])
            if row[1] == "MaxPoint":
                self.MaxPoint = int(row[2])

        # veritabanı bağlantısını kapat
        conn.close()
        
    def update_app_parameters(self, parameter_name, parameter_value):
        conn = sqlite3.connect(self.DatabasePath)
        cursor = conn.cursor()
        
        cursor.execute("UPDATE app_parameters SET value = ? WHERE name = ?",
                        (str(parameter_value), parameter_name))
        conn.commit()

        conn.close()
    
    def sync_recording(self):
        # veritabanı bağlantısını aç
        conn = sqlite3.connect(self.DatabasePath)
        cursor = conn.cursor()

        # değerleri sorgula
        cursor.execute("SELECT * from operations Where start_date is not null and stop_date is null ")
        rows = cursor.fetchall()

        if len(rows) != 0:
            self.OperationWorking = 1       

        # veritabanı bağlantısını kapat
        conn.close()    
        
    def update_ui(self,socketio):
        while True:
            socketio.emit('data', {'isRecording': self.DefaultRecording or self.OperationWorking ,
                                   'currentTime': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

                                    )
            socketio.sleep(1)   
                
globalVars = GlobalVars()




