# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt

def load_pint(filename):
    pressures = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('#') or not line:
                continue
            parts = line.split()
            if len(parts) >= 2 and parts[0].isdigit():
                pressures.append(float(parts[1]))
    return np.array(pressures)

p_cam6    = load_pint('pint.CAM6.txt')
p_cam7lt  = load_pint('pint.CAM7-LT.txt')
p_cam7mt  = load_pint('pint.CAM7-MT.txt')
p_waccm6  = load_pint('pint.WACCM6.txt')

print("Surface pressures:")
print(f"CAM6:    {p_cam6[0]:.1f} Pa")
print(f"CAM7-LT: {p_cam7lt[0]:.1f} Pa")
print(f"CAM7-MT: {p_cam7mt[0]:.1f} Pa")
print(f"WACCM6:  {p_waccm6[0]:.1f} Pa")

def compute_dz_height(p_surface_to_top):
    p = p_surface_to_top[::-1]   # top to surface
    
    R = 287.058
    g = 9.80665
    T_mean = 255.0
    
    z = np.zeros(len(p))
    for i in range(1, len(p)):
        z[i] = z[i-1] + (R * T_mean / g) * np.log(p[i-1] / p[i]) / 1000.0
    
    dz_m = np.diff(z) * 1000.0
    z_mid_km = (z[:-1] + z[1:]) / 2
    
    return z_mid_km, dz_m

# Compute
z_cam6,    dz_cam6    = compute_dz_height(p_cam6)
z_cam7lt,  dz_cam7lt  = compute_dz_height(p_cam7lt)
z_cam7mt,  dz_cam7mt  = compute_dz_height(p_cam7mt)
z_waccm6,  dz_waccm6  = compute_dz_height(p_waccm6)

print(f"\nFirst dz values (m):")
print(f"CAM6:    {dz_cam6[0]:.1f}")
print(f"CAM7-LT: {dz_cam7lt[0]:.1f}")
print(f"CAM7-MT: {dz_cam7mt[0]:.1f}")
print(f"WACCM6:  {dz_waccm6[0]:.1f}")


# ====================== TWO-PANEL PLOT ======================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

colors = ['#e41a1c', '#377eb8', '#4daf4a']#, '#984ea3']
labels = ['CAM6 (32L)', 'CAM7-LT (58L)', 'CAM7-MT (93L)']#, 'WACCM6 (71L)']
datasets = [(dz_cam6, z_cam6), (dz_cam7lt, z_cam7lt), (dz_cam7mt, z_cam7mt)]#, (dz_waccm6, z_waccm6)]

for i, (dz, z) in enumerate(datasets):
    ax1.plot(dz, z, label=labels[i], lw=2.2, color=colors[i],
             marker='o', markersize=6, markerfacecolor='none', markeredgewidth=1.4)
    ax2.plot(dz, z, label=labels[i], lw=2.2, color=colors[i],
             marker='o', markersize=6, markerfacecolor='none', markeredgewidth=1.4)

# Panel (a) - Full range
ax1.set_xlabel('Grid spacing dz (m)', fontsize=16)
ax1.set_ylabel('Height (km)', fontsize=16)
ax1.set_xlim(0, 8000)
ax1.set_ylim(0, 90)
ax1.grid(True, alpha=0.35)
ax1.set_title('(a) Full vertical range', fontsize=20)

# Panel (b) - Near-surface zoom
ax2.set_xlabel('Grid spacing dz (m)', fontsize=16)
ax2.set_ylabel('Height (km)', fontsize=16)
ax2.set_xlim(0, 500)
ax2.set_ylim(0, 2)
ax2.grid(True, alpha=0.35)
ax2.set_title('(b) Near-surface zoom (0-2 km)', fontsize=20)

ax1.legend(fontsize=20, loc='lower right')

# Make axis numbers (tick labels) LARGER
ax1.tick_params(axis='both', which='major', labelsize=16)
ax2.tick_params(axis='both', which='major', labelsize=16)

plt.suptitle('Layer Thickness (dz) versus Height', fontsize=20)
plt.tight_layout(rect=[0, 0, 1, 0.94])
plt.savefig('dz_vs_height_panels.png', dpi=400, bbox_inches='tight')
plt.show()

print("\nPlot saved as dz_vs_height_panels.png")


# ====================== PLOT ======================
fig, ax1 = plt.subplots(figsize=(11, 9))

colors = ['#e41a1c', '#377eb8', '#4daf4a',]# '#984ea3']
labels = ['CAM6 (32L)', 'CAM7-LT (~58L)', 'CAM7-MT (93L)']#, 'WACCM6 (70L)']
datasets = [(dz_cam6, z_cam6), (dz_cam7lt, z_cam7lt), (dz_cam7mt, z_cam7mt)]#, (dz_waccm6, z_waccm6)]

for i, (dz, z) in enumerate(datasets):
    ax1.plot(dz, z, label=labels[i], lw=2.2, color=colors[i],
             marker='o', markersize=6, markerfacecolor='none', markeredgewidth=1.4)

ax1.set_xlabel('Grid spacing dz (m)', fontsize=13)
ax1.set_ylabel('Height (km)', fontsize=13)
ax1.set_xlim(0, 8000)
#ax1.set_ylim(0, 145)
ax1.set_ylim(0, 90)
ax1.grid(True, alpha=0.35)

ax2 = ax1.twinx()
ax2.set_yscale('log')
ax2.set_ylabel('Pressure (hPa)', fontsize=13)
ax2.set_ylim(1000, 0.001)

ax1.legend(fontsize=11, loc='upper left')



plt.title('Layer Thickness (dz) versus Height', fontsize=14)
plt.tight_layout()
plt.savefig('dz_vs_height_final.png', dpi=400, bbox_inches='tight')
plt.show()
