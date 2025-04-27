import os
import xml.etree.ElementTree as ET
import numpy as np
import matplotlib.pyplot as plt

# Ruta base de las simulaciones
base_path = "outputs/threads_1000"

# Número de hilos que se probaron
thread_values = [1, 2, 4, 8, 10, 12]

# Diccionario para almacenar los tiempos de ejecución
execution_times = {threads: [] for threads in thread_values}

# Extraer tiempos de ejecución desde los archivos final.xml
for threads in thread_values:
    for rep in range(1, 11):  # 10 repeticiones por configuración
        folder = f"{base_path}/threads_{threads}_rep{rep}"
        xml_file = os.path.join(folder, "final.xml")

        if os.path.exists(xml_file):
            tree = ET.parse(xml_file)
            root = tree.getroot()
            runtime_elem = root.find(".//current_runtime")
            if runtime_elem is not None:
                execution_time = float(runtime_elem.text)
                execution_times[threads].append(execution_time)

# Calcular promedio y desviación estándar
avg_times = []
std_times = []

print("\n=== Execution Time Summary ===")
for threads in thread_values:
    times = execution_times[threads]
    if times:  # Evitar errores si no hay datos
        avg = np.mean(times)
        std = np.std(times)
        avg_times.append(avg)
        std_times.append(std)
        
        # Imprimir los valores
        print(f"\nThreads: {threads}")
        print(f"Times: {times}")
        print(f"Mean: {avg:.4f} sec, Std Dev: {std:.4f} sec")
    else:
        avg_times.append(None)
        std_times.append(None)
        print(f"\nThreads: {threads} - No data found")

# Graficar comparación de tiempos de ejecución
plt.figure(figsize=(8, 5))
plt.errorbar(thread_values, avg_times, yerr=std_times, fmt='o-', capsize=5, 
             color="#007acc", ecolor="#cc0000", elinewidth=2, capthick=2, markersize=8, lw=2, label="Execution Time")

# Agregar anotaciones en los puntos
for i, txt in enumerate(avg_times):
    plt.annotate(f"{txt:.2f} s", (thread_values[i], avg_times[i]), textcoords="offset points", xytext=(0, 10),
                 ha="center", fontsize=10, color="black", weight="bold")

# Mejoras en los ejes y el estilo general
plt.xlabel("Number of Threads", fontsize=12, fontweight="bold")
plt.ylabel("Execution Time (seconds)", fontsize=12, fontweight="bold")
plt.title("Execution Time (1000 initial tumor cells) vs Number of Threads", fontsize=14, fontweight="bold")
plt.xticks(thread_values, fontsize=11)
plt.yticks(fontsize=11)
plt.grid(True, linestyle="--", alpha=0.6)
plt.legend(fontsize=11)
plt.tight_layout()

# Guardar la imagen en alta calidad
# plt.savefig("execution_time_vs_threads_1000.png", dpi=300)

plt.show()  # Descomentar si quieres ver la gráfica
