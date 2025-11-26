import pandas as pd

# Ruta al archivo Excel
archivo = 'ventas.xlsm'

# Leer la hoja "Ventas"
df = pd.read_excel(archivo, sheet_name='Ventas', engine='openpyxl')

# Mostrar los primeros registros (opcional)
print(df.head())

# Convertir a JSON
json_resultado = df.to_json(orient='records', force_ascii=False)

# Guardar el JSON en un archivo
with open('datos_dashboard.json', 'w', encoding='utf-8') as f:
    f.write(json_resultado)

print("✅ JSON generado correctamente como 'datos_dashboard.json'")