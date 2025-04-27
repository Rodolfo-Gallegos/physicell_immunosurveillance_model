import pandas as pd
import subprocess
import shutil
import os
import xml.etree.ElementTree as ET

# Rutas de configuración
xml_path = "config/PhysiCell_settings.xml"
csv_path = "config/cell_rules.csv"
# initial_mesh_path = "outputs/initial_mesh0.mat"

# Factores para multiplicar los valores base
half_max_factors = [0.2, 0.5, 2.0, 5.0]

# Reglas a modificar
rules_to_modify = [
    ("naive T cell", "IL-10", "decreases", "transform to CD8 T cell"),  # Rule1
    ("naive T cell", "IFN-gamma", "increases", "transform to CD8 T cell"),  # Rule2
    ("CD8 T cell", "IL-10", "increases", "transform to exhausted T cell"),  # Rule3
    ("CD8 T cell", "IL-10", "decreases", "attack tumor"),  # Rule4
    ("M0 Macrophage", "contact with dead cell", "increases", "transform to M1 Macrophage"), # Rule5
    ("M0 Macrophage", "IFN-gamma", "increases", "transform to M1 Macrophage"), # Rule6
    ("M0 Macrophage", "IL-10", "increases", "transform to M2 Macrophage"), # Rule7
    ("M0 Macrophage", "IL-4", "increases", "transform to M2 Macrophage"), # Rule8
    ("M1 Macrophage", "IL-4", "increases", "transform to M2 Macrophage"), # Rule9
    ("M2 Macrophage", "IFN-gamma", "increases", "transform to M1 Macrophage") # Rule10
]

# Valores base
base_values = {
    rules_to_modify[0]: 0.25,
    rules_to_modify[1]: 0.25,
    rules_to_modify[2]: 0.5,  
    rules_to_modify[3]: 0.25,
    rules_to_modify[4]: 0.1,
    rules_to_modify[5]: 0.1,
    rules_to_modify[6]: 0.1,  
    rules_to_modify[7]: 0.1,
    rules_to_modify[8]: 5.0,  
    rules_to_modify[9]: 5.0,
}

# Repeticiones
num_replicates = 10

# Función para modificar el CSV
def modify_and_save_csv(half_max_changes, save_path):
    df = pd.read_csv(csv_path, header=None)
    for idx, row in df.iterrows():
        key = tuple(row[:4])
        if key in half_max_changes:
            df.at[idx, 5] = half_max_changes[key]
    df.to_csv(save_path, index=False, header=False)

# Repeticiones externas
for rep in range(1, num_replicates + 1):
    # Cambios individuales
    for param_idx, param in enumerate(rules_to_modify):
        for factor in half_max_factors:
            half_max_changes = base_values.copy()
            half_max_changes[param] = base_values[param] * factor
            folder = f"/media/rodolfo/FE761CFD761CB7FB/Ubuntu/outputs/MPSA_1000/rule{param_idx + 1}_HM{factor}_rep{rep}"
            
            if os.path.exists(folder):
                print(f"Skipping existing simulation: {folder}")
                continue

            os.makedirs(folder, exist_ok=True)
            tree = ET.parse(xml_path)
            root = tree.getroot()
            root.find(".//save/folder").text = folder
            tree.write(xml_path)
            modify_and_save_csv(half_max_changes, csv_path)
            shutil.copy(csv_path, os.path.join(folder, "cell_rules.csv"))
            # shutil.copy(initial_mesh_path, folder)
            subprocess.run(["./project"])

    # Comparaciones de pares
    for i in range(len(rules_to_modify)):
        for j in range(i + 1, len(rules_to_modify)):
            for factor_i in half_max_factors:
                for factor_j in half_max_factors:
                    half_max_changes = base_values.copy()
                    half_max_changes[rules_to_modify[i]] = base_values[rules_to_modify[i]] * factor_i
                    half_max_changes[rules_to_modify[j]] = base_values[rules_to_modify[j]] * factor_j
                    folder = f"/media/rodolfo/FE761CFD761CB7FB/Ubuntu/outputs/MPSA_1000/rule{i + 1}_vs_rule{j + 1}_HM{factor_i}_{factor_j}_rep{rep}"

                    if os.path.exists(folder):
                        print(f"Skipping existing simulation: {folder}")
                        continue
                    
                    os.makedirs(folder, exist_ok=True)
                    tree = ET.parse(xml_path)
                    root = tree.getroot()
                    root.find(".//save/folder").text = folder
                    tree.write(xml_path)
                    modify_and_save_csv(half_max_changes, csv_path)
                    shutil.copy(csv_path, os.path.join(folder, "cell_rules.csv"))
                    # shutil.copy(initial_mesh_path, folder)
                    subprocess.run(["./project"])

print("\nAll sensitivity simulations completed.")
