#!/usr/bin/env python3
"""
2x2 panel plot of surface pressure for the moist baroclinic wave test.

Usage:
    python plot_PS_contour.py <day>        # physical simulation day 1–15
    python plot_PS_contour.py 10 --save
"""

import sys
import argparse
import numpy as np
import xarray as xr
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cmaps

# Publication-quality defaults
plt.rcParams.update({
    "font.family":      "sans-serif",
    "font.size":        13,
    "axes.titlesize":   14,
    "axes.labelsize":   12,
    "xtick.labelsize":  11,
    "ytick.labelsize":  11,
    "xtick.direction":  "out",
    "ytick.direction":  "out",
    "xtick.major.size": 4,
    "ytick.major.size": 4,
    "axes.linewidth":   0.8,
})

ncview_cmap = cmaps.ncview_default

parser = argparse.ArgumentParser()
parser.add_argument("day", type=int, help="Physical simulation day (1–15)")
parser.add_argument("--save", action="store_true")
parser.add_argument("--format", choices=["pdf", "png"], default="pdf",
                    help="Output format when --save is used (default: pdf)")
args = parser.parse_args()

# Data timestamps are end-of-day labels (Jan 2 = end of simulation day 1, etc.)
available_days = list(range(1, 16))
if args.day not in available_days:
    sys.exit(f"Day {args.day} not available. Choose from {available_days}.")
idx = args.day - 1

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
base = "/glade/campaign/cgd/amp/pel/src/cam7-paper-stuff/fig/baroclinic-wave"

def load_roll(path, var, time_dim, lat_dim, lon_dim, time_idx):
    """Load a field and roll longitude from 0–360 to -180–180 if needed."""
    ds = xr.open_dataset(path)
    ps = ds[var].isel({time_dim: time_idx}).values / 100.0  # Pa → hPa
    lat = ds[lat_dim].values
    lon = ds[lon_dim].values
    if lon.max() > 180:
        nlon = len(lon)
        roll = nlon // 2
        lon = np.where(lon >= 180, lon - 360, lon)
        lon = np.roll(lon, roll)
        ps = np.roll(ps, roll, axis=1)
    return lat, lon, ps

lat,    lon,    ps_new = load_roll(f"{base}/new_PS.nc",  "PS", "time", "lat",      "lon",       idx)
_,      _,      ps_old = load_roll(f"{base}/old_PS.nc",  "PS", "time", "lat",      "lon",       idx)
lat_ne, lon_ne, ps_ne  = load_roll(f"{base}/ne30np4.nc", "PS", "time", "lat",      "lon",       idx)
lat_mp, lon_mp, ps_mp  = load_roll(f"{base}/mpas.nc",    "PS", "Time", "latitude", "longitude", idx)

# ---------------------------------------------------------------------------
# Color scale and contour levels: fixed to 999–1001 hPa
# ---------------------------------------------------------------------------
vmin, vmax = 999.0, 1001.0
norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
noise_levels = np.arange(999.0, 1001.01, 0.2)

# ---------------------------------------------------------------------------
# Plot — 2×2 grid, pure matplotlib
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(16, 10))

panels = [
    (axes[0, 0], "Biharmonic wv damping after CSLAM→GLL interp (ne30pg3)", "(a)", lat,    lon,    ps_new),
    (axes[0, 1], "No damping after CSLAM→GLL interp (ne30pg3)",             "(b)", lat,    lon,    ps_old),
    (axes[1, 0], "no-CSLAM (ne30np4)",                                      "(c)", lat_ne, lon_ne, ps_ne),
    (axes[1, 1], "MPAS",                                                     "(d)", lat_mp, lon_mp, ps_mp),
]

pm_ref = None
for ax, title, label, la, lo, ps in panels:
    pm = ax.pcolormesh(lo, la, ps, norm=norm, cmap=ncview_cmap, shading="auto", rasterized=True)
    if pm_ref is None:
        pm_ref = pm
    ax.contour(lo, la, ps, levels=noise_levels, colors="k", linewidths=0.7)
    ax.text(0.02, 0.97, label, transform=ax.transAxes,
            fontsize=13, fontweight="bold", va="top", ha="left",
            bbox=dict(facecolor="white", edgecolor="black", boxstyle="square,pad=0.3"))
    ax.set_title(title, fontsize=14, pad=6)
    ax.set_xlabel("Longitude", labelpad=3)
    ax.set_ylabel("Latitude", labelpad=3)
    ax.set_xlim(-180, 180)
    ax.set_ylim(la.min(), la.max())
    ax.set_xticks(np.arange(-180, 181, 60))
    ax.set_yticks(np.arange(-90, 91, 30))
    ax.tick_params(which="both", top=True, right=True)

fig.subplots_adjust(left=0.07, right=0.85, top=0.93, bottom=0.07, wspace=0.15, hspace=0.28)

# Manually placed colorbar so bbox_inches="tight" doesn't squeeze it
cbar_ax = fig.add_axes([0.88, 0.1, 0.018, 0.78])  # [left, bottom, width, height]
cbar = fig.colorbar(pm_ref, cax=cbar_ax, orientation="vertical", extend="both")
cbar.set_label("Surface Pressure (hPa)", fontsize=13, labelpad=8)
cbar.ax.tick_params(labelsize=11)

fig.suptitle(
    f"Moist baroclinic wave surface pressure — Day {args.day}"
    f"  |  black contours: 999–1001 hPa every 0.2 hPa",
    fontsize=15, fontweight="bold", y=1.01,
)

if args.save:
    out = f"{base}/PS_day{args.day:02d}.{args.format}"
    dpi = 200 if args.format == "png" else None  # PDF is vector, dpi irrelevant
    fig.savefig(out, dpi=dpi, bbox_inches="tight")
    print(f"Saved: {out}")
else:
    plt.show()
