import os
import xml.etree.ElementTree as ET
import numpy as np
import matplotlib.pyplot as plt

# Ruta base de las simulaciones
base_path = "outputs/threads_1000"

# Número de hilos que se probaron
thread_values = [1, 2, 4, 8]

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

# Colors for line and error bars
line_color = "#1f77b4"     # Soft blue
error_color = "#ff7f0e"    # Orange for error bars

plt.figure(figsize=(8, 5))

# Line with markers and error bars
plt.errorbar(thread_values, avg_times, yerr=std_times, fmt='o-', capsize=6, 
             color=line_color, ecolor=error_color, elinewidth=2, capthick=1.5, 
             markersize=9, lw=2.5, label="Execution time")

# Annotations above each point with adjusted x offset for specific cases
for i, txt in enumerate(avg_times):
    x_offset = 35 if thread_values[i] in [2, 4] else 0  # Shift right for 2 and 4 threads
    plt.annotate(f"{txt:.2f} s", (thread_values[i], avg_times[i]),
                 textcoords="offset points", xytext=(x_offset, 10),
                 ha="center", fontsize=14, color="black", weight="semibold")

# Labels and title
plt.xlabel("Number of cores", fontsize=18, fontweight="bold")
plt.ylabel("Execution time (seconds)", fontsize=18, fontweight="bold")
plt.title("Execution time vs Number of cores\n(1000 initial tumor cells)", 
          fontsize=18, fontweight="bold", pad=15)

# Axis formatting
plt.xticks(thread_values, fontsize=14)
plt.yticks(fontsize=14)
plt.grid(True, which='major', linestyle='--', alpha=0.5)
plt.box(False)  # Clean style

# Legend
plt.legend(loc="upper right", fontsize=18, frameon=False)

# Layout and export
plt.tight_layout()
# plt.savefig("execution_time_vs_threads_1000.png", dpi=300)
plt.show()
