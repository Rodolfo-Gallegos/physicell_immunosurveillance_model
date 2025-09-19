import os
import shutil
import subprocess
import xml.etree.ElementTree as ET

# Configuration files and associated output folders
configs = [
    ("PhysiCell_settings (1000tc).xml", "1_cores_1000"),
    ("PhysiCell_settings (2000tc).xml", "2_cores_2000"),
    ("PhysiCell_settings (4000tc).xml", "4_cores_4000"),
    ("PhysiCell_settings (8000tc).xml", "8_cores_8000"),
]

# Path to the active configuration file
xml_path = "config/PhysiCell_settings.xml"

# Number of replicates
num_replicates = 30

# Optional LD_PRELOAD
env = os.environ.copy()
use_jemalloc = True
if use_jemalloc:
    env["LD_PRELOAD"] = "/usr/local/lib/libjemalloc.so"

# Function to modify the output folder in the XML
def modify_output_folder(new_folder):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    root.find(".//save/folder").text = new_folder
    tree.write(xml_path)

# Loop over each configuration
for config_file, output_dir in configs:
    # Copy the configuration file as PhysiCell_settings.xml
    src = os.path.join("config", config_file)
    shutil.copy(src, xml_path)
    print(f"\n=== Running {config_file} → {output_dir} ===")

    # Replicates
    for rep in range(1, num_replicates + 1):
        new_folder = f"outputs/ROPEC_Optimized/Weak/{output_dir}/rep_{rep}"

        if os.path.exists(new_folder):
            print(f"Skipping existing simulation: {new_folder}")
            continue

        os.makedirs(new_folder, exist_ok=True)

        # Update output folder in XML
        modify_output_folder(new_folder)

        # Run the project
        subprocess.run(["./project"], env=env)

print("\n✅ All simulations completed.")
