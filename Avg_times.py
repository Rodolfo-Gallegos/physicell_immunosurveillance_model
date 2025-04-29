import csv
import os
import math

# Función para leer el CSV de cada simulación y extraer los datos
def read_parallel_timings(rep_folder):
    file_path = os.path.join(rep_folder, "parallel_timings.csv")
    timings = {}
    
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            section = row["Seccion"]
            time = float(row["Tiempo(segundos)"])
            percentage = float(row["Porcentaje(%)"])
            timings[section] = (time, percentage)
    
    return timings

# Función para calcular el promedio y desviación estándar de una lista de valores
def calculate_avg_and_std(values):
    n = len(values)
    if n == 0:
        return 0.0, 0.0
    avg = sum(values) / n
    std_dev = math.sqrt(sum((x - avg) ** 2 for x in values) / n) if n > 1 else 0.0
    return avg, std_dev

# Carpeta donde se encuentran las simulaciones
base_folder = "outputs/tiempos_icpx"
num_reps = 10

# Lista para almacenar todos los datos de cada repetición
all_timings = {}

# Leer los archivos de todas las repeticiones
for rep in range(1, num_reps + 1):
    rep_folder = os.path.join(base_folder, f"rep_{rep}")
    timings = read_parallel_timings(rep_folder)
    all_timings[rep] = timings

# Crear el archivo CSV donde se combinarán todos los tiempos, porcentajes, y cálculos
output_file = base_folder +"/combined_parallel_timings_with_avg_std.csv"
with open(output_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    
    # Escribir la cabecera
    header = ["Seccion"] + [f"Rep_{i}_Tiempo" for i in range(1, num_reps + 1)] + [f"Rep_{i}_Porcentaje" for i in range(1, num_reps + 1)] + ["Avg_Tiempo", "Avg_Porcentaje", "StdDev_Tiempo", "StdDev_Porcentaje"]
    writer.writerow(header)
    
    # Escribir los datos
    sections = next(iter(all_timings.values())).keys()  # Obtener las secciones de la primera repetición
    for section in sections:
        row = [section]
        
        # Listas para calcular los promedios y desviaciones estándar
        tiempos = []
        porcentajes = []
        
        for rep in range(1, num_reps + 1):
            time, percentage = all_timings[rep].get(section, (0, 0))
            row.append(time)
            row.append(percentage)
            tiempos.append(time)
            porcentajes.append(percentage)
        
        # Calcular el promedio y desviación estándar
        avg_time, std_time = calculate_avg_and_std(tiempos)
        avg_percentage, std_percentage = calculate_avg_and_std(porcentajes)
        
        # Añadir los resultados de promedio y desviación estándar a la fila
        row.extend([avg_time, avg_percentage, std_time, std_percentage])
        
        writer.writerow(row)

print(f"CSV combinado con promedios y desviaciones estándar guardado en: {output_file}")
