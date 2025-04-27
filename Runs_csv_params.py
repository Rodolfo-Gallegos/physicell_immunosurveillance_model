import pandas as pd
import subprocess
import shutil
import os
import xml.etree.ElementTree as ET

# Ruta del archivo de configuración XML
xml_path = "config/PhysiCell_settings.xml"

# Ruta del archivo de configuración CSV
csv_path = "config/cell_rules.csv"

# Ruta de la carpeta con las posiciones iniciales
# initial_mesh_path = "outputs/initial_mesh0.mat"

# Valores de Half-max a probar
half_max_values = [0.1, 0.25, 0.05, 1.0]

# Filas a modificar
rules_to_modify = [
    ("naive T cell", "IL-10", "decreases", "transform to CD8 T cell"),
    ("naive T cell", "IFN-gamma", "increases", "transform to CD8 T cell"),
    ("CD8 T cell", "IL-10", "increases", "transform to exhausted T cell")
]

# Número de repeticiones por combinación
num_replicates = 3

sim_id = 0  # Contador de simulaciones


def modify_and_save_csv(half_max_changes, save_path):
    df = pd.read_csv(csv_path, header=None)  # El archivo no tiene encabezado
    
    # Modificar los valores de Half-max
    for idx, row in df.iterrows():
        if tuple(row[:4]) in rules_to_modify:  # Comparar las primeras 4 columnas
            df.at[idx, 5] = half_max_changes[tuple(row[:4])]
    
    # Guardar el CSV modificado
    df.to_csv(save_path, index=False, header=False)


for half_max_1 in half_max_values:
    for half_max_2 in half_max_values:
        for half_max_3 in half_max_values:
            for rep in range(num_replicates):
                
                new_folder = f"outputs/CFJ_rules/output_HM1_{half_max_1}_HM2_{half_max_2}_HM3_{half_max_3}_rep{rep}"
                
                # Si la carpeta ya existe, omitir esta simulación
                if os.path.exists(new_folder):
                    print(f"Skipping existing simulation: {new_folder}")
                    continue

                os.makedirs(new_folder, exist_ok=True)
                
                # Leer el XML
                tree = ET.parse(xml_path)
                root = tree.getroot()
                
                # Modificar la carpeta de salida
                folder = root.find(".//save/folder")
                if folder is not None:
                    folder.text = new_folder
                    
                # Guardar los cambios en el XML
                tree.write(xml_path)

                # Crear diccionario con los valores de Half-max a modificar
                half_max_changes = {
                    rules_to_modify[0]: half_max_1,
                    rules_to_modify[1]: half_max_2,
                    rules_to_modify[2]: half_max_3,
                }

                # Modificar y sobrescribir el CSV original
                modify_and_save_csv(half_max_changes, csv_path)
                
                # Copiar el archivo CSV modificado a la carpeta de salida
                shutil.copy(csv_path, os.path.join(new_folder, "cell_rules.csv"))
                
                # Copiar el archivo initial_mesh0.mat a la nueva carpeta
                # shutil.copy(initial_mesh_path, new_folder)
                
                print(f"Running simulation {sim_id+1} with HM1={half_max_1}, HM2={half_max_2}, HM3={half_max_3}, output folder: {new_folder}")
                
                # Ejecutar PhysiCell
                subprocess.run(["./project"])
                
                sim_id += 1

print("\nAll simulations completed.")
