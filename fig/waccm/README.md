# Explicit damping/sponge figures (del4, del2, vertical-diffusion sponge)

`plot_del4_damping.py` parses the damping tables that the SE dycore prints at
initialization in the atm log (`k,pmid_ref,z,nu_lev,nu_t_lev,nu_p_lev,nu_div_lev`
and the sponge-layer Laplacian table) and plots:

- the del4 (hyperviscosity) coefficients `nu` (= `nu_t` = `nu_p`) and `nu_div`
  (bottom x-axis, linear, 10^15 m^4 s^-1),
- the del2 sponge-layer Laplacian damping (`nu_top`-based) and the
  vertical-diffusion sponge `diff_sponge_fac * kvm_sponge` (shared log top
  x-axis, m^2 s^-1),
- vs reference pressure (left) and US-standard-atmosphere height (right);
  circles mark model levels.

The vertical-diffusion sponge profile `kvm_sponge` is hardcoded in
`src/atmos_phys/schemes/vertical_diffusion/vertical_diffusion_sponge_layer.F90`
(selected by `ptop_ref`); `diff_sponge_fac` is parsed from the log so the plot
shows the coefficient actually applied.

Usage:

```
python plot_del4_damping.py [logs-dir-or-atm-log] [-o out.pdf] [--title T] [--nu-top X]
```

`--nu-top X` re-synthesizes the del2 sponge as `nu_scale_top * X` (the
level-dependent `nu_scale_top` profile depends only on the model-top location,
not on `nu_top`).

## Figures and the namelist settings they correspond to

### del4_damping_profile.pdf — WACCM7 (L135, this paper's configuration)

Case: `f.e30.FHISTC_WAma.ne30pg3_mg17_L135_cam6_4_201_ctr_polartaper.nutop1e7only`
(ne30pg3, 135 levels, model top 2.04e-4 Pa, damping configuration `top_090_140km`).

| Namelist variable | Value in `atm_in` | Resolved value used by the model |
|---|---|---|
| `se_nu_top` | 1.0e7 | nu_top = 1.0e7 m^2/s; level profile nu_scale_top = 5, 5, 5, 2, 1, 0.1 (k = 1..6) → del2 sponge = 5e7, 5e7, 5e7, 2e7, 1e7, 1e6 m^2/s |
| `se_nu` | -1 (default) | nu = 1.0e15 m^4/s (automatically set from resolution) |
| `se_nu_div` | -1 (default) | nu_div = 2.5e15 m^4/s |
| `se_nu_p` | -1 (default) | nu_p = 1.0e15 m^4/s (nu_t follows nu) |
| `se_sponge_del4_nu_fac` | -1 (default) | 5.0 (top-of-model del4 ramp: nu ramps to 5.0e15) |
| `se_sponge_del4_nu_div_fac` | -1 (default) | 7.5 (nu_div ramps to 7.5e15) |
| `se_sponge_del4_lev` | -1 (default) | 20 (ramp tapers to interior values near level 20, ~3 hPa / ~73 km) |
| `diff_sponge_fac` | 0.1 | vertical-diffusion sponge = 0.1 × kvm_sponge = 2e4, 2e4, 1.5e4, 1e4, 5e3, 1e3 m^2/s (top 6 interfaces; high-top profile, ptop_ref < 1e-3 Pa) |

### del4_damping_profile_nutop1e6.pdf — WACCM7 with default nu_top

Identical to the above except the del2 sponge curve is synthesized with the
CAM default `se_nu_top = 1.0e6` (no archived run; generated with
`--nu-top 1e6`, i.e. del2 sponge = nu_scale_top × 1e6 = 5e6, 5e6, 5e6, 2e6,
1e6, 1e5 m^2/s). All del4 coefficients and the vertical-diffusion sponge are
unchanged (they do not depend on `nu_top`).

### del4_damping_profile_MT.pdf — CAM7 MT defaults

Case: `f.e30_gll_double_adv.FHISTC_MTso.ne30_nirvana.001` (C. Hannay;
`/glade/derecho/scratch/hannay/archive/`), ne30 GLL, 93 levels, model top
0.43 Pa. All damping settings are the CAM7 MT defaults:

| Namelist variable | Value in `atm_in` | Resolved value used by the model |
|---|---|---|
| `se_nu_top` | -1 (default) | nu_top = 1.0e6 m^2/s; 4-level sponge, del2 sponge up to 5e6 m^2/s at the top level |
| `se_nu` | -1 (default) | nu = 1.0e15 m^4/s |
| `se_nu_div` | -1 (default) | nu_div = 2.5e15 m^4/s |
| `se_nu_p` | -1 (default) | nu_p = 1.0e15 m^4/s |
| `se_sponge_del4_nu_fac` | -1 (default) | 3.4 (nu ramps to 3.4e15) |
| `se_sponge_del4_nu_div_fac` | -1 (default) | 3.4 (nu_div ramps to 3.4e15) |
| `se_sponge_del4_lev` | -1 (default) | 4 |
| `diff_sponge_fac` | 0.0 (default) | no vertical-diffusion sponge (curve omitted from the plot) |

## Notes

- The atm log's printout "vertical diffusion coefficient at interface k is
  increased by ..." lists the *unscaled* `kvm_sponge` values; the
  `diff_sponge_fac` multiplier is applied in the run phase
  (`vertical_diffusion_sponge_layer_run`). The plots show the scaled
  (actually applied) coefficients.
- Heights are the dycore's barometric-formula values (US standard atmosphere)
  printed in the same log tables; the right-hand axis ticks are placed by
  interpolating that z(p) relation.
