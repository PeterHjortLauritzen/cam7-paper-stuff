# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

def load_levels(filename):
    data = np.loadtxt(filename, skiprows=1, usecols=(0, 2))
    level = data[:, 0].astype(int)
    height_km = data[:, 1] / 1000.0
    return level, height_km

# Load data
levels_cam6,   z_cam6   = load_levels('cam6.txt')
levels_cam7lt, z_cam7lt = load_levels('cam7-lt.txt')
levels_cam7mt, z_cam7mt = load_levels('cam7-mt.txt')

models = [
    ('CAM6',   levels_cam6,   z_cam6),
    ('CAM7-LT', levels_cam7lt, z_cam7lt),
    ('CAM7-MT', levels_cam7mt, z_cam7mt)
]

fig = plt.figure(figsize=(18, 12))
gs = GridSpec(2, 3, figure=fig, hspace=0.08, wspace=0.25)

for col, (title, levels, z) in enumerate(models):
    color = 'tab:blue'
    
    # Top subplot: 5 km to 80 km (linear)
    ax_top = fig.add_subplot(gs[0, col])
    for i in range(len(z)):
        if z[i] > 5.0:
            ax_top.hlines(z[i], 0, 1, colors=color, linewidth=2.2)
            # Label INSIDE the plot, next to the line
            ax_top.text(1.02, z[i], f'{levels[i]}', va='center', ha='left', fontsize=11)
    
    ax_top.set_title(title, fontsize=15)
    ax_top.set_ylim(5.0, 80.0)          # fixed to 80 km for all models
    ax_top.set_xlim(0, 1)
    ax_top.grid(True, alpha=0.3, linestyle='--')
    ax_top.set_xticks([])

    # Bottom subplot: 0-5 km (log scale)
    ax_bottom = fig.add_subplot(gs[1, col])
    for i in range(len(z)):
        if z[i] <= 5.0:
            ax_bottom.hlines(z[i], 0, 1, colors=color, linewidth=2.2)
            # Label INSIDE the plot, next to the line
            ax_bottom.text(1.02, z[i], f'{levels[i]}', va='center', ha='left', fontsize=11)
    
    ax_bottom.set_yscale('log')
    ax_bottom.set_ylim(0.05, 5.0)
    ax_bottom.set_yticks([0.1, 0.2, 0.5, 1.0, 2.0, 5.0])
    ax_bottom.set_yticklabels(['0.1','0.2','0.5','1','2','5'])
    ax_bottom.set_xlim(0, 1)
    ax_bottom.grid(True, alpha=0.3, linestyle='--')
    ax_bottom.set_xticks([])

    # Y-labels only on left column
    if col == 0:
        ax_top.set_ylabel('Height (km)', fontsize=14)
        ax_bottom.set_ylabel('Height (km)', fontsize=14)

plt.suptitle('Height of Model Levels with Scale Break', fontsize=17, y=0.96)
plt.tight_layout(rect=[0, 0, 1, 0.94])
plt.savefig('model_level_heights_3columns_split.png', dpi=450, bbox_inches='tight')
plt.show()

print("Plot saved as model_level_heights_3columns_split.png")
