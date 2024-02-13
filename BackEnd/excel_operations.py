import pandas as pd
from io import BytesIO

def create_excel_file(rows):
    df = pd.DataFrame(rows, columns=['Datetime', 'CO', 'CO2', 'CH4'])
    excel_file = BytesIO()
    df.to_excel(excel_file, index=False)
    excel_file.seek(0)
    return excel_file