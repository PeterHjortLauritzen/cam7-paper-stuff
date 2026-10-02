#!/usr/bin/env python
"""Plot vertical profiles of the del4 (hyperviscosity) damping coefficients
in WACCM/CAM-SE, parsed from the atm log file.

The dycore prints a table at initialization:

    z computed from barometric formula (using US std atmosphere)
    k,pmid_ref,z,nu_lev,nu_t_lev,nu_p_lev,nu_div_lev
     1 0.6140E-03 0.1380E+06 0.5000E+16 ...

Usage:
    python plot_del4_damping.py [LOGDIR_OR_FILE] [-o OUTPUT.pdf]

LOGDIR_OR_FILE may be a case logs/ directory (the newest atm.log*.gz is
used), a specific atm log (gzipped or plain), or omitted to use the
default case below.
"""

import argparse
import glob
import gzip
import os
import re
import sys

import matplotlib.pyplot as plt
import numpy as np

DEFAULT_LOGDIR = (
    "/glade/derecho/scratch/pel/archive/"
    "f.e30.FHISTC_WAma.ne30pg3_mg17_L135_cam6_4_201_ctr_polartaper.nutop1e7only/logs"
)

TABLE_HEADER = "k,pmid_ref,z,nu_lev,nu_t_lev,nu_p_lev,nu_div_lev"
DEL2_HEADER = "k, p, z, nu_scale_top, nu (actual Laplacian damping coefficient)"

# Vertical-diffusion sponge (m^2/s), top interfaces
# (vertical_diffusion_sponge_layer.F90); applied as diff_sponge_fac * kvm_sponge.
# High-top profile for ptop_ref < 1e-3 Pa (WACCM), low-top otherwise (CAM MT/LT).
KVM_SPONGE_HIGHTOP = np.array([2.0e5, 2.0e5, 1.5e5, 1.0e5, 0.5e5, 0.1e5])
KVM_SPONGE_LOWTOP = np.array([2.0e4, 2.0e4, 0.5e4, 0.1e4])
DIFF_SPONGE_FAC_LINE = "Sponge layer vertical diffusion factor:"
PTOP_REF_RE = re.compile(r"\(ptop_ref\s*=\s*([0-9.DdEe+-]+)\s*Pa\)")


def resolve_logfile(path):
    """Return the atm log file to read: newest atm.log*.gz if a directory."""
    if os.path.isdir(path):
        candidates = sorted(glob.glob(os.path.join(path, "atm.log*")))
        if not candidates:
            sys.exit(f"No atm.log* files found in {path}")
        return candidates[-1]
    if os.path.isfile(path):
        return path
    sys.exit(f"No such file or directory: {path}")


def read_tables(logfile):
    """Parse the del4 and del2 (sponge Laplacian) damping tables.

    Returns (del4, del2) dicts of 1-D arrays; keeps the last occurrence of
    each table in the log.
    """
    opener = gzip.open if logfile.endswith(".gz") else open
    rows4, rows2 = [], []
    in4 = in2 = False
    diff_sponge_fac = None
    ptop_ref = None
    with opener(logfile, "rt") as f:
        for line in f:
            if DIFF_SPONGE_FAC_LINE in line:
                diff_sponge_fac = float(line.split(":")[1])
                continue
            m = PTOP_REF_RE.search(line)
            if m:
                ptop_ref = float(m.group(1).replace("D", "E"))
                continue
            if TABLE_HEADER in line:
                in4, rows4 = True, []
                continue
            if DEL2_HEADER in line:
                in2, rows2 = True, []
                continue
            parts = line.split()
            if in4:
                if len(parts) == 7 and re.match(r"\d+$", parts[0]):
                    rows4.append([float(p) for p in parts])
                else:
                    in4 = False
            if in2:
                if len(parts) == 5 and re.match(r"\d+$", parts[0]):
                    rows2.append([float(p) for p in parts])
                else:
                    in2 = False
    if not rows4:
        sys.exit(f"del4 table ('{TABLE_HEADER}') not found in {logfile}")
    if not rows2:
        sys.exit(f"del2 sponge table ('{DEL2_HEADER}') not found in {logfile}")
    arr4 = np.array(rows4)
    del4 = {
        "k": arr4[:, 0].astype(int),
        "pmid": arr4[:, 1],       # Pa
        "z": arr4[:, 2],          # m
        "nu": arr4[:, 3],         # m^4/s
        "nu_t": arr4[:, 4],
        "nu_p": arr4[:, 5],
        "nu_div": arr4[:, 6],
    }
    arr2 = np.array(rows2)
    del2 = {
        "k": arr2[:, 0].astype(int),
        "pmid": arr2[:, 1],       # Pa
        "z": arr2[:, 2],          # m
        "nu_scale_top": arr2[:, 3],
        "nu": arr2[:, 4],         # m^2/s
    }
    if diff_sponge_fac is None:
        sys.exit(f"'{DIFF_SPONGE_FAC_LINE}' not found in {logfile}")
    if ptop_ref is None:
        sys.exit(f"ptop_ref not found in {logfile}")
    kvm_sponge = diff_sponge_fac * (
        KVM_SPONGE_HIGHTOP if ptop_ref < 1.0e-3 else KVM_SPONGE_LOWTOP)
    return del4, del2, kvm_sponge


def plot_profiles(d4, d2, kvm_sponge, output, title="WACCM7"):
    scale4 = 1.0e15   # m^4/s

    fig, ax = plt.subplots(figsize=(4.6, 5.8))

    p_hpa = d4["pmid"] / 100.0

    # del4 curves (bottom x-axis); nu = nu_t = nu_p -> one curve
    h_nu, = ax.plot(
        d4["nu"] / scale4, p_hpa,
        color="#2a78d6", linestyle="-", linewidth=1.6,
        marker="o", markersize=4.0, markerfacecolor="none",
        markeredgecolor="#2a78d6", markeredgewidth=0.9,
        label=r"$\nu,\,\nu_T,\,\nu_p$  ($\nabla^4$)", clip_on=False,
    )
    h_div, = ax.plot(
        d4["nu_div"] / scale4, p_hpa,
        color="#e34948", linestyle="-", linewidth=1.6,
        marker="o", markersize=4.0, markerfacecolor="none",
        markeredgecolor="#e34948", markeredgewidth=0.9,
        label=r"$\nu_{\mathrm{div}}$  ($\nabla^4$)", clip_on=False,
    )

    ax.set_yscale("log")
    ax.invert_yaxis()
    ax.set_ylim(1.1e3, 0.9 * p_hpa.min())
    ax.set_xlim(left=0)
    ax.set_xlabel(r"$\nabla^4$ damping coefficient ($10^{15}$ m$^4$ s$^{-1}$)")
    ax.set_ylabel("Reference pressure (hPa)")

    # diffusion sponges on their own x-scale (log top axis, m^2/s):
    # horizontal del2 (nu_top) and vertical diffusion (kvm_sponge)
    ax2 = ax.twiny()
    p2_hpa = d2["pmid"] / 100.0
    h_del2, = ax2.plot(
        d2["nu"], p2_hpa,
        color="#008300", linestyle="--", linewidth=1.6,
        marker="o", markersize=4.0, markerfacecolor="none",
        markeredgecolor="#008300", markeredgewidth=0.9,
        label=r"$\nu_{\mathrm{top}}$ sponge  ($\nabla^2$)", clip_on=False,
    )
    handles = [h_nu, h_div, h_del2]
    if np.any(kvm_sponge > 0.0):
        h_kvm, = ax2.plot(
            kvm_sponge, d4["pmid"][: len(kvm_sponge)] / 100.0,
            color="#eb6834", linestyle="-.", linewidth=1.6,
            marker="o", markersize=4.0, markerfacecolor="none",
            markeredgecolor="#eb6834", markeredgewidth=0.9,
            label=r"$k_{vm}$ sponge  (vert. diff.)", clip_on=False,
        )
        handles.append(h_kvm)
    ax2.set_xscale("log")
    ax2.set_xlim(5.0e2, 1.0e8)
    ax2.set_xlabel(r"Diffusion coefficient (m$^2$ s$^{-1}$)",
                   color="#008300")
    ax2.tick_params(axis="x", which="both", colors="#008300", direction="out")
    ax2.spines["top"].set_color("#008300")
    for side in ("bottom", "left", "right"):
        ax2.spines[side].set_visible(False)

    # right-hand height axis: fixed ticks at round heights, placed at the
    # pressure of that height from the log's z(p) profile
    logp = np.log(d4["pmid"])
    z_km = d4["z"] / 1000.0
    z_ticks = np.array([0, 20, 40, 60, 80, 100, 120])
    z_ticks = z_ticks[z_ticks <= z_km.max()]
    p_ticks = np.exp(np.interp(z_ticks, z_km[::-1], logp[::-1])) / 100.0

    axr = ax.twinx()
    axr.set_yscale("log")
    axr.set_ylim(ax.get_ylim())
    axr.set_yticks(p_ticks)
    axr.set_yticklabels([f"{z:d}" for z in z_ticks])
    axr.minorticks_off()
    axr.set_ylabel("Height (km)")
    axr.tick_params(direction="out")
    for side in ("top", "left", "bottom"):
        axr.spines[side].set_visible(False)
    axr.spines["right"].set_color("#c3c2b7")

    ax.grid(True, which="major", color="#e1e0d9", linewidth=0.6)
    ax.tick_params(direction="out", which="both")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color("#c3c2b7")

    ax.legend(handles=handles, frameon=False,
              loc="best", fontsize=9, handlelength=2.6)

    if title:
        ax.set_title(title, fontsize=12, pad=30)

    fig.tight_layout()
    fig.savefig(output)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(
        description="Plot WACCM del4 damping-coefficient profiles from an atm log."
    )
    parser.add_argument(
        "logpath", nargs="?", default=DEFAULT_LOGDIR,
        help="case logs/ directory or a specific atm log file "
             f"(default: {DEFAULT_LOGDIR})",
    )
    parser.add_argument(
        "-o", "--output", default="del4_damping_profile.pdf",
        help="output PDF filename (default: %(default)s)",
    )
    parser.add_argument(
        "--title", default="WACCM7",
        help="plot title (default: %(default)s)",
    )
    parser.add_argument(
        "--nu-top", type=float, default=None,
        help="override nu_top (m^2/s): del2 sponge coefficient becomes "
             "nu_scale_top * NU_TOP instead of the value in the log",
    )
    args = parser.parse_args()

    logfile = resolve_logfile(args.logpath)
    print(f"Reading damping tables from {logfile}")
    d4, d2, kvm_sponge = read_tables(logfile)
    print(f"Parsed {len(d4['k'])} del4 levels "
          f"(p = {d4['pmid'][0]:.3e} ... {d4['pmid'][-1]:.3e} Pa); "
          f"{len(d2['k'])} del2 sponge levels; "
          f"kvm sponge (incl. diff_sponge_fac) = {kvm_sponge}")

    if args.nu_top is not None:
        d2["nu"] = d2["nu_scale_top"] * args.nu_top
        print(f"Overriding nu_top: del2 sponge = nu_scale_top * {args.nu_top:.1e}")

    plot_profiles(d4, d2, kvm_sponge, args.output, title=args.title)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
