import os
import sqlite3

class GlobalVars :
    def __init__(self) :
        self.DatabasePath = os.path.join(os.getcwd(), "BackEnd", "users.db")
                       
        self.CO_Read = 00.00
        self.CO2_Read = 0.000
        self.CH4_Read = 00.00
        
        self.CO_Offset = 00.00
        self.CO2_Offset = 00.00
        self.CH4_Offset = 00.00
        
        self.CO_Result = 00.00
        self.CO2_Result = 00.00
        self.CH4_Result = 00.00
        
        self.X = 0
        self.Y = 0
        self.Z = 0
        
        self.load_offsets()
        self.load_live_constant()
    
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
        # Veritabanı bağlantısını aç
        conn = sqlite3.connect(self.DatabasePath)
        cursor = conn.cursor()

        # OFFSET değerlerini sorgula
        cursor.execute("SELECT Temperature, CH4Factor,AlloyFactor,H2 FROM livetabledatas")
        rows = cursor.fetchall()

        # OFFSET değerlerini sınıf özelliklerine ata
        for Temperature, CH4Factor, AlloyFactor, H2 in rows:
            self.Temp = Temperature
            self.CH4Factor = CH4Factor
            self.AlloyFactor = AlloyFactor
            self.H2 = H2

        # Veritabanı bağlantısını kapat
        conn.close()
            
globalVars = GlobalVars()



