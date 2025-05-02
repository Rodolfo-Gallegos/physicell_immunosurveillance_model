import os
import xml.etree.ElementTree as ET
import numpy as np
import matplotlib.pyplot as plt

# Carpeta base
base_dir = "outputs/weak"
configs = ["1c_500tc", "2c_1000tc", "4c_2000tc", "8c_4000tc"]

# Listas para gráficas
cores = []
tumor_cells = []
avg_times = []
std_times = []

# Leer tiempos
for config in configs:
    num_cores = int(config.split("c_")[0])
    tc = int(config.split("_")[1].replace("tc", ""))
    
    runtimes = []
    for rep in range(1, 11):
        xml_path = os.path.join(base_dir, config, f"rep_{rep}", "final.xml")
        if os.path.exists(xml_path):
            tree = ET.parse(xml_path)
            root = tree.getroot()
            runtime_elem = root.find(".//current_runtime")
            if runtime_elem is not None:
                runtimes.append(float(runtime_elem.text))
    
    if runtimes:
        cores.append(num_cores)
        tumor_cells.append(tc)
        avg_times.append(np.mean(runtimes))
        std_times.append(np.std(runtimes))

# Imprimir tabla de resultados
print(f"{'Config':<15}{'Cores':<10}{'Tumor Cells':<15}{'Avg Time (s)':<15}{'Std Dev (s)':<15}")
print("-" * 70)
for config, core, tc, avg, std in zip(configs, cores, tumor_cells, avg_times, std_times):
    print(f"{config:<15}{core:<10}{tc:<15}{avg:<15.2f}{std:<15.2f}")


# Graficar
fig, ax1 = plt.subplots(figsize=(8, 5))

# Gráfica de tiempo promedio (eje izquierdo)
ax1.errorbar(cores, avg_times, yerr=std_times, fmt='o-', color="#00BECC",
             capsize=6, lw=2.5, label="Execution Time (avg ± std)")

ax1.set_xlabel("Number of Cores", fontsize=18, fontweight="bold")
ax1.set_ylabel("Execution Time (seconds)", fontsize=18, fontweight="bold", color="#00BECC")
ax1.tick_params(axis='y', labelcolor="#00BECC", labelsize=14)
ax1.tick_params(axis='x', labelsize=14)
ax1.set_xticks(cores)
ax1.set_ylim(bottom=0)
ax1.grid(True, linestyle="--", alpha=0.6)


# Eje derecho para número de células tumorales
ax2 = ax1.twinx()
ax2.bar(cores, tumor_cells, alpha=0.8, width=0.6, color="#67001F", label="Initial Tumor Cells")
ax2.set_ylabel("Initial Tumor Cells", fontsize=18, fontweight="bold", color="#67001F")
ax2.tick_params(axis='y', labelcolor="#67001F", labelsize=14)

# Leyendas y layout
plt.box(False)  # Clean style
fig.legend(loc="upper left", bbox_to_anchor=(0.12, 0.9), fontsize=14)
plt.title("Weak scaling", fontsize=18, fontweight="bold")
plt.tight_layout()
plt.show()
