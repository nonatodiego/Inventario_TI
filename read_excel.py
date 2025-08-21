import pandas as pd

excel_file = '/home/ubuntu/upload/Planilha_Ativos_TI.xlsx'
df = pd.read_excel(excel_file)

print(df.to_json(orient='records', indent=4))

