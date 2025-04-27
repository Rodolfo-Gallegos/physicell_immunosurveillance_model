import matplotlib.pyplot as plt
import numpy as np

# Datos de tiempo promedio
threads = [1, 2, 4, 8, 10, 12]
time_1000 = [321.5952, 186.7143, 114.7724, 79.3884, 87.5954, 89.5704]
time_2000 = [624.9852, 332.3780, 180.9363, 124.2344, 146.7364, 131.6475]

# Posiciones de las barras en el eje x
x = np.arange(len(threads))
width = 0.35  # Ancho de las barras

fig, ax = plt.subplots(figsize=(8, 6))

# Crear las barras, colocando 2000 primero y luego 1000
bars2 = ax.bar(x - width/2, time_2000, width, label='2000 Tumor Cells', color='tab:blue')  # A la izquierda
bars1 = ax.bar(x + width/2, time_1000, width, label='1000 Tumor Cells', color='tab:orange')  # A la derecha

# Etiquetas y título
ax.set_xlabel('Number of Threads')
ax.set_ylabel('Simulation Time (sec)')
ax.set_title('Weak Scalability: Simulation Time vs Threads')
ax.set_xticks(x)
ax.set_xticklabels(threads)
ax.legend()

# Agregar valores encima de las barras y líneas horizontales
for bar1, bar2 in zip(bars1, bars2):
    height1 = bar1.get_height()
    height2 = bar2.get_height()

    # Etiquetas de valores en la parte superior de cada barra
    ax.annotate(f'{height2:.1f}',
                xy=(bar2.get_x() + bar2.get_width() / 2, height2),
                xytext=(0, 3), textcoords="offset points",
                ha='center', va='bottom', fontsize=10, color='black')

    ax.annotate(f'{height1:.1f}',
                xy=(bar1.get_x() + bar1.get_width() / 2, height1),
                xytext=(0, 3), textcoords="offset points",
                ha='center', va='bottom', fontsize=10, color='black')

plt.tight_layout()
plt.show()
