import os
import subprocess
import xml.etree.ElementTree as ET

# Ruta del archivo de configuración (XML/HTML)
html_path = "config/PhysiCell_settings.xml"

# Número de hilos a probar
thread_values = [1, 2, 4, 8, 10, 12]

# Número de repeticiones
num_replicates = 10

# Función para modificar el número de hilos en el archivo XML/HTML
def modify_num_threads(num_threads):
    tree = ET.parse(html_path)
    root = tree.getroot()
    parallel_elem = root.find(".//parallel/omp_num_threads")
    if parallel_elem is not None:
        parallel_elem.text = str(num_threads)
        tree.write(html_path)

# Bucle externo para iterar sobre los hilos
for num_threads in thread_values:
    modify_num_threads(num_threads)  # Modificar el número de hilos en el HTML

    # Bucle de repeticiones
    for rep in range(1, num_replicates + 1):
        new_folder = f"outputs/threads_1000/threads_{num_threads}_rep{rep}"
        
        if os.path.exists(new_folder):
            print(f"Skipping existing simulation: {new_folder}")
            continue  

        os.makedirs(new_folder, exist_ok=True)

        # Modificar la carpeta de salida en el XML
        tree = ET.parse(html_path)
        root = tree.getroot()
        root.find(".//save/folder").text = new_folder
        tree.write(html_path)

        # Ejecutar la simulación
        subprocess.run(["./project"])

print("\n✅ All simulations completed.")
