import os

class GlobalVars :
    def __init__(self) :
        self.DatabasePath = os.path.join(os.getcwd(), "BackEnd", "users.db")
               
        
        self.CO_Read = 00.00
        self.CO2_Read = 0.000
        self.CH4_Read = 00.00
        
        self.CO_Offset = 00.00
        self.CO2_Offset = 00.00
        self.CH4_Offset = 00.00
        
        self.CO_Result = self.CO_Read + self.CO_Offset
        print('CO_Read:',self.CO_Read)
        # self.CO2_Result = self.CO2_Read + self.CO2_Offset
        # self.CH4_Result = self.CH4_Read + self.CH4_Offset
        
globalVars = GlobalVars()

