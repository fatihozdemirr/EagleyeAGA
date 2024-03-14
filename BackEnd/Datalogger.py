import sqlite3
import threading
from datetime import datetime, timedelta
import time
from GlobalVars import globalVars


def insert_data():
    conn = sqlite3.connect(globalVars.DatabasePath)
    c = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute('INSERT INTO datalogger (Datetime, CO, CO2, CH4) VALUES (?, ?, ?, ?)',
              (now, globalVars.CO_Result, globalVars.CO2_Result, globalVars.CH4_Result))
    conn.commit()
    conn.close()
    
def get_data(start_date, end_date):
    conn = sqlite3.connect(globalVars.DatabasePath)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute('SELECT Datetime, CO, CO2, CH4 FROM datalogger WHERE Datetime BETWEEN ? AND ?', (start_date, end_date))
    rows = cur.fetchall()
    conn.close()

    return rows

def get_last_constant_data(point_count):
    # Veritabanı bağlantısını aç
    conn = sqlite3.connect(globalVars.DatabasePath)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor() 
   
    # Toplam geriye gidilecek saniye = point sayısı * her bir kayıt arasındaki saniye
    #total_seconds_back = point_count * globalVars.RecordInterval
    
    # Minimum tarihi hesapla (şimdiki zamandan 'total_seconds_back' saniye önce)
    #min_datetime = datetime.now() - timedelta(seconds=total_seconds_back)
    
    # Minimum tarihten itibaren olan kayıtları al
    #cur.execute('SELECT Datetime, CO, CO2, CH4 FROM datalogger WHERE Datetime > ?', (min_datetime.strftime('%Y-%m-%d %H:%M:%S'),))
    cur.execute('SELECT Datetime, CO, CO2, CH4 FROM (SELECT Datetime, CO, CO2, CH4 FROM datalogger WHERE Datetime <= ? ORDER BY Datetime DESC LIMIT ?) ORDER BY Datetime ASC', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), point_count))


    rows = cur.fetchall()

    # Veritabanı bağlantısını kapat
    conn.close()

    # Sonuçları döndür
    return rows

class DataLogger:
    def __init__(self):
        self._running = False
        self._thread = None

    def _run(self):
        while self._running:
            insert_data()
            time.sleep(globalVars.RecordInterval)

    def start(self):
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self._run)
            
            self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join()
            
    def get_data(self, start_date, end_date):
        return get_data(start_date, end_date)
    
    def get_last_constant_data(self, point):
        return get_last_constant_data(point)

dataLogger = DataLogger()
if globalVars.OperationWorking or globalVars.DefaultRecording:
    dataLogger.start()