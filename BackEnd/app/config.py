from GlobalVars import globalVars

class Config:
    SECRET_KEY = 'secret!'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + globalVars.DatabasePath 
