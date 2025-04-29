import os
import subprocess
import xml.etree.ElementTree as ET

# Ruta del archivo de configuración (XML/HTML)
html_path = "config/PhysiCell_settings.xml"

# Número de repeticiones
num_replicates = 10

# Función para modificar la carpeta de salida en el archivo XML
def modify_output_folder(new_folder):
    tree = ET.parse(html_path)
    root = tree.getroot()
    root.find(".//save/folder").text = new_folder
    tree.write(html_path)

# Bucle de repeticiones
for rep in range(1, num_replicates + 1):
    new_folder = f"outputs/tiempos_icpx/rep_{rep}"
    
    if os.path.exists(new_folder):
        print(f"Skipping existing simulation: {new_folder}")
        continue  

    os.makedirs(new_folder, exist_ok=True)

    # Modificar la carpeta de salida en el XML
    modify_output_folder(new_folder)

    # Ejecutar la simulación
    subprocess.run(["./project"])

print("\n✅ All simulations completed.")
