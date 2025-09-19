import os
import subprocess
import xml.etree.ElementTree as ET

# Path to the configuration file (XML/HTML)
xml_path = "config/PhysiCell_settings.xml"

# Define environment with LD_PRELOAD
env = os.environ.copy()
use_jemalloc = True
if use_jemalloc:
    env["LD_PRELOAD"] = "/usr/local/lib/libjemalloc.so"

# Number of threads to test
thread_values = [1, 2, 4, 8]

# Number of replicates
num_replicates = 30

# Function to modify the number of threads in the XML/HTML file
def modify_num_threads(num_threads):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    parallel_elem = root.find(".//parallel/omp_num_threads")
    if parallel_elem is not None:
        parallel_elem.text = str(num_threads)
        tree.write(xml_path)

# Outer loop to iterate over thread counts
for num_threads in thread_values:
    modify_num_threads(num_threads)  # Modify number of threads in XML

    # Replicates loop
    for rep in range(1, num_replicates + 1):
        # new_folder = f"outputs/threads_1000_poster/threads_{num_threads}_rep{rep}"
        
        new_folder = f"outputs/ROPEC_Optimized/Strong/threads_{num_threads}_rep{rep}_"
        
        if os.path.exists(new_folder):
            print(f"Skipping existing simulation: {new_folder}")
            continue  

        os.makedirs(new_folder, exist_ok=True)

        # Modify output folder in XML
        tree = ET.parse(xml_path)
        root = tree.getroot()
        root.find(".//save/folder").text = new_folder
        tree.write(xml_path)

        # Run the binary with the specified environment
        subprocess.run(["./project"], env=env)

print("\n✅ All simulations completed.")
