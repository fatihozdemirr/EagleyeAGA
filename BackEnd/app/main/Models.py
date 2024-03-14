from app import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)   
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(120), nullable=False)
    timezone = db.Column(db.String(50), nullable=True)
    
class LiveTableDatas(db.Model):
    __tablename__ = 'livetabledatas'
    id = db.Column(db.Integer, primary_key=True)
    TempUnit = db.Column(db.String(80), nullable=False)
    Temperature = db.Column(db.Integer, nullable=False)
    CH4Factor = db.Column(db.Integer, nullable=False)
    AlloyFactor = db.Column(db.Integer,  nullable=False)
    H2 = db.Column(db.Integer,  nullable=False)
    
class CalibrationTableDatas(db.Model):
    __tablename__ = 'calibration'
    id = db.Column(db.Integer, primary_key=True)
    GAS = db.Column(db.String, nullable=False)
    OFFSET = db.Column(db.Float, nullable=False)
    READING = db.Column(db.Float, nullable=False)
    VALUE = db.Column(db.Float,  nullable=False)
    
class Operations(db.Model):
    __tablename__ = 'operations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    company = db.Column(db.String(50), nullable=False)
    furnace = db.Column(db.String(20), nullable=False)
    operator = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.DateTime, nullable=True)
    stop_date = db.Column(db.DateTime, nullable=True)
    
class CalibrationLogs(db.Model):
    __tablename__ = 'calibration_logs'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    calibration_type = db.Column(db.String(50), nullable=False)
    old_value = db.Column(db.String(80), nullable=False)
    calibration_value = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    
class SensorReferanceValues(db.Model):
    __tablename__ = 'sensorreferance'
    id = db.Column(db.Integer, primary_key=True)
    COReferance = db.Column(db.Integer, nullable=False)
    CO2Referance = db.Column(db.Integer, nullable=False)
    CH4Referance = db.Column(db.Integer,  nullable=False)
 
   
class AppParameter(db.Model):
    __tablename__ = 'app_parameters'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    value = db.Column(db.String(200), nullable=False)
    
