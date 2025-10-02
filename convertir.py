import pandas as pd
import os

# Ruta al archivo Excel
archivo_xlsx = "C:\\Users\\saave\\Desktop\\horarios\\Reporte Mayo 2025.xlsx"

# Carpeta de salida
carpeta_salida = "C:\\Users\\saave\\Desktop\\horarios\\Reporte Mayo 2025"
#os.makedirs(carpeta_salida, exist_ok=True)

# Cargar todas las hojas
xlsx = pd.ExcelFile(archivo_xlsx)

# Recorrer cada hoja
i = 0
for nombre_hoja in xlsx.sheet_names[2:]:
    # Leer hoja
    df = pd.read_excel(archivo_xlsx, sheet_name=nombre_hoja)
    
    # Crear nombre para el CSV
    nombre_csv = os.path.join(carpeta_salida, f"asistencia{i}.csv")
    
    # Guardar como CSV
    df.to_csv(nombre_csv, index=False, encoding="utf-8-sig")
    print(f"✅ Hoja '{nombre_hoja}' exportada a: {nombre_csv}")
    i = i+1
