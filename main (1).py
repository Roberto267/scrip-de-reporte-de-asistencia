import pandas as pd
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import glob

# Inicializar Firebase
#aqui poner la que te de firebase en configuracion de proyecto esta en el apartado de general.

# Definir mes con año 
mes = "septiembre 2025"

# Funciones para conversión horas <-> minutos
def horas_a_minutos(hm):
    h, m = hm.replace("m","").split("h")
    return int(h)*60 + int(m)

def minutos_a_horas(mins):
    h, m = divmod(mins, 60)
    return f"{h}h{m:02d}m"

# Obtener todos los archivos CSV de asistencia existentes
archivos = sorted(glob.glob("F:\\CUCEI\\Instituto\\Prestadores de Servicio Social\\2025\\Reporte Septiembre 2025\\csv\\asistencia*.csv"))

# Guardar todos los datos para mostrar y eventualmente subir
empleados_datos = {}

for archivo_actual in archivos:
    df = pd.read_csv(archivo_actual, header=None)

    bloques = [(0, 9), (15, 24), (30, 39)]
    for inicio, fin in bloques:
        val = df.iloc[2, inicio+9]
        if isinstance(val, str) and val.strip() != "":
            nombre = val.strip()
            if nombre not in empleados_datos:
                empleados_datos[nombre] = df.iloc[11:, inicio:fin]

def calcular_horas_por_dia(df):
    resultados = {}
    incompletos = []
    for _, row in df.iterrows():
        fecha = row.iloc[0]
        minutos_dia = 0
        horas = [h for h in row[1:] if isinstance(h, str) and ":" in h]
        for i in range(0, min(len(horas), 4), 2):
            try:
                t1 = datetime.strptime(horas[i], "%H:%M")
                t2 = datetime.strptime(horas[i+1], "%H:%M")
                minutos_dia += (t2 - t1).seconds // 60
            except Exception:
                incompletos.append(fecha)
                continue
        if minutos_dia > 0:
            h, m = divmod(minutos_dia, 60)
            resultados[fecha] = f"{h}h{m:02d}m"
    return resultados, incompletos

# 🔹 Mostrar todos los datos primero
todos_empleados = {}
for nombre, df_emp in empleados_datos.items():
    horas, incompletos = calcular_horas_por_dia(df_emp)
    total_minutos = sum(horas_a_minutos(hm) for hm in horas.values())
    total_str = minutos_a_horas(total_minutos)

    print(f"\n{nombre}:")
    for dia, hm in horas.items():
        print(f"  {dia}: {hm}")
    th, tm = divmod(total_minutos, 60)
    print(f"  Total: {th}h{tm:02d}m")
    if incompletos:
        print(f"⚠ Días con pares incompletos: {', '.join(incompletos)}")

    # Guardar para subir luego si se confirma
    todos_empleados[nombre] = total_str

# 🔹 Preguntar si desea subir todos los datos a Firebase
respuesta = input("\n¿Deseas subir todos los datos a Firebase? (s/n): ").strip().lower()
if respuesta == "s":
    for nombre, total_str in todos_empleados.items():
        doc_ref = db.collection("Asistencia-del-servicio").document(nombre)
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            meses = data.get("meses", {})

            # permitir mismo mes si es distinto año ---
            mes_nombre, mes_anio = mes.split()  

            ya_existe = False
            for mes_guardado in meses.keys():
                guardado_nombre, guardado_anio = mes_guardado.split()
                if guardado_nombre == mes_nombre and guardado_anio == mes_anio:
                    ya_existe = True
                    break

            if not ya_existe:
                meses[mes] = total_str
                doc_ref.set({
                    "meses": meses,
                    "carrera": data.get("carrera", ""),
                    "area": data.get("area", ""),
                    "nombre": data.get("nombre", "")
                }, merge=True)
            else:
                print(f"⚠ El mes '{mes}' ya fue subido para {nombre}, no se suman horas.")
        else:
            doc_ref.set({
                "meses": {mes: total_str},
                "carrera": "",
                "area": "",
                "nombre": ""   
            })
    print("\n✅ Todos los datos fueron subidos a Firebase.")
else:

    print("\n❌ Ningún dato fue subido a Firebase.")
