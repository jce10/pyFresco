#!/usr/bin/env python3
import os
import glob
import argparse

import numpy as np
import matplotlib.pyplot as plt

# Your existing scripts (must be in the same directory / PYTHONPATH)
import merge
import lmfit_chi_squared as lmf

from lmfit import Model, Parameters
from sigfig import round as sig_round
import re

CFG_TO_L = {"p": "1", "d": "2", "f": "3", "g": "4"}

CFG_TO_ORBIT = {
    "2p32": "2p3/2",
    "2d52": "2d5/2",
    "1f52": "1f5/2",
    "1f72": "1f7/2",
    "1g92": "1g9/2",
}


def parse_inp_for_cfgs_and_J(inp_basename: str):
    """
    Handles names like:
      48Ti_5158_2p32_4+.inp
      48Ti_5158_2p32_4+_7.6kG.inp
      48Ti_5158_2p32_1f52_4+.inp
      48Ti_5158_2p32_1f52_4+_7.6kG.inp
    Returns: (cfgs_list, J_int_or_None)
    """
    stem = os.path.basename(inp_basename).replace(".inp", "")
    toks = stem.split("_")

    # configs: tokens containing p/d/f/g
    cfgs = [t for t in toks if any(c in t for c in ["p", "d", "f", "g"])]

    # J: token like '4+' or '3-' (ignore suffix tokens like '7.6kG')
    J = None
    for t in toks:
        m = re.fullmatch(r"(\d+)([+-])", t)
        if m:
            J = int(m.group(1))
            break

    return cfgs, J


def cfgs_to_L_transfer(cfgs):
    # mixed like ["2p32","1f52"] -> "1+3"
    l_list = []
    for cfg in cfgs:
        # find which letter (p/d/f/g) is in cfg
        letter = next((ch for ch in ["p","d","f","g"] if ch in cfg), None)
        if letter is None:
            continue
        l_list.append(CFG_TO_L[letter])
    return "+".join(l_list)


def cfgs_to_orbit_string(cfgs):
    # ["2p32"] -> "2p3/2", ["2p32","1f52"] -> "2p3/2+1f5/2"
    parts = []
    for cfg in cfgs:
        parts.append(CFG_TO_ORBIT.get(cfg, cfg))
    return "+".join(parts)


def panel_key_from_inp(inp_name: str) -> str:
    base = os.path.basename(inp_name).replace(".inp", "")
    toks = base.split("_")
    cfgs = [t for t in toks if any(c in t for c in ["p", "d", "f", "g"])]
    if len(cfgs) == 1:
        return cfgs[0]
    elif len(cfgs) == 2:
        return f"{cfgs[0]}_{cfgs[1]}"
    return "unknown"


def find_exp_file(angular_dir: str, energy: int) -> str:
    # Prefer exact-ish matches with delimiters
    patterns = [
        os.path.join(angular_dir, f"*_{energy}_*.txt"),
        os.path.join(angular_dir, f"*_{energy}.txt"),
        os.path.join(angular_dir, f"*{energy}*keV*.txt"),
        os.path.join(angular_dir, f"*{energy}*.txt"),  # last resort
    ]

    matches = []
    for p in patterns:
        matches = sorted(glob.glob(p))
        if matches:
            return matches[0]

    raise FileNotFoundError(f"No experimental .txt found in {angular_dir} for energy {energy}.")



def build_theory_map(fresco_dir: str, energy: int) -> dict:
    files = sorted(glob.glob(os.path.join(fresco_dir, f"*_{energy}_*.sorted")))
    if not files:
        raise FileNotFoundError(f"No .sorted files found in {fresco_dir} matching '*_{energy}_*.sorted'.")

    cfg_map = {}
    for f in files:
        base = os.path.basename(f)
        toks = base.split("_")
        if len(toks) < 3:
            continue
        cfg = toks[2]
        cfg_map[cfg] = base
    return cfg_map


def inp_name_for_files(fresco_files: list[str]) -> str:
    if len(fresco_files) == 1:
        return os.path.splitext(fresco_files[0])[0] + ".inp"

    f1 = os.path.splitext(fresco_files[0])[0]
    f2 = os.path.splitext(fresco_files[1])[0]
    fname1 = f1.split("_")
    fname2 = f2.split("_")
    finalName = "_".join(fname1[:3] + fname2[2:])
    return finalName + ".inp"


def run_fit_on_inp(inp_path: str, ax=None, panel_label=None):
    data = np.loadtxt(inp_path)
    energy = os.path.basename(inp_path).split("_")[1]
    print(f"\n=== Starting Chi-Squared for {energy} keV from: {os.path.basename(inp_path)} ===")

    if data.ndim == 1:
        data = data.reshape(1, -1)

    # -------------------- single --------------------
    if data.shape[1] == 4:
        MIXED = False
        angles, x_sec_vals, error_vals, fresco_vals = np.transpose(data)

        valid = (x_sec_vals > 0) & (error_vals > 0) & ~np.isnan(x_sec_vals) & ~np.isnan(error_vals)
        angles = angles[valid]
        x_sec_vals = x_sec_vals[valid]
        error_vals = error_vals[valid]
        fresco_vals = fresco_vals[valid]

        model = Model(lmf.ADWA_Fit)
        params = Parameters()
        params.add("SF", value=0.1)

        result = model.fit(x_sec_vals, x=np.asarray(fresco_vals), params=params, weights=1.0 / error_vals)

        lmf.plot_data(
            MIXED, result, angles, x_sec_vals, error_vals, fresco_vals, energy,
            inp_name=os.path.basename(inp_path),
            ax=ax,
            panel_label=panel_label
        )

        return {
            "label": os.path.basename(inp_path),
            "mixed": False,
            "redchi": result.redchi,
            "chisqr": result.chisqr,
            "params": {k: (v.value, v.stderr) for k, v in result.params.items()},
        }

    # -------------------- mixed --------------------
    elif data.shape[1] == 5:
        MIXED = True
        angles, x_sec_vals, error_vals, f1, f2 = np.transpose(data)

        valid = (x_sec_vals > 0) & (error_vals > 0) & ~np.isnan(x_sec_vals) & ~np.isnan(error_vals)
        angles = angles[valid]
        x_sec_vals = x_sec_vals[valid]
        error_vals = error_vals[valid]
        f1 = f1[valid]
        f2 = f2[valid]

        combined = np.array([f1, f2])

        model = Model(lmf.ADWA_Mixed_Fit)
        params = Parameters()
        params.add("SF1", 0.5, min=0.0001, max=1.0)
        params.add("SF2", 0.5, min=0.0001, max=1.0)

        result = model.fit(x_sec_vals, x=combined, params=params, weights=1.0 / error_vals)

        lmf.plot_data(
            MIXED, result, angles, x_sec_vals, error_vals, combined, energy,
            inp_name=os.path.basename(inp_path),
            ax=ax,
            panel_label=panel_label
        )

        return {
            "label": os.path.basename(inp_path),
            "mixed": True,
            "redchi": result.redchi,
            "chisqr": result.chisqr,
            "params": {k: (v.value, v.stderr) for k, v in result.params.items()},
        }

    else:
        raise ValueError(f"Unexpected number of columns in {inp_path}: {data.shape[1]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("energy", type=int, help="State energy in keV, e.g. 7155")
    ap.add_argument("--base", default=os.getcwd(), help="chi_squared_fitting base dir (default: cwd)")
    args = ap.parse_args()

    base = os.path.abspath(args.base)
    fresco_dir = os.path.join(base, "fresco_output_files")
    angular_dir = os.path.join(base, "angular_dist_folder")
    minimizing_dir = os.path.join(base, "minimizing_folder")

    for d in (fresco_dir, angular_dir, minimizing_dir):
        if not os.path.isdir(d):
            raise FileNotFoundError(f"Missing required directory: {d}")

    energy = args.energy
    exp_file = find_exp_file(angular_dir, energy)
    print(f"Experimental file: {exp_file}")

    cfg_map = build_theory_map(fresco_dir, energy)
    print(f"Found {len(cfg_map)} theory configs for {energy} keV.")
    # ---------------------------------------------------------
    # Decide which f-orbit to use for ell = 3 (1f5/2 OR 1f7/2)
    # ---------------------------------------------------------
    if "1f52" in cfg_map:
        f_cfg = "1f52"
    elif "1f72" in cfg_map:
        f_cfg = "1f72"
    else:
        f_cfg = None
        print(f"WARNING: no ell=3 theory file found at {energy} keV")

    # ---------------------------------------------------------
    # Build panel layout dynamically using chosen f-orbit
    # ---------------------------------------------------------
    panel_order = [
        "2p32",
        "2d52",
        f_cfg,
        "1g92",
        f"2p32_{f_cfg}" if f_cfg else None,
        "2d52_1g92",
    ]

    panel_labels = {
        "2p32": "p",
        "2d52": "d",
        f_cfg: "f",
        "1g92": "g",
        f"2p32_{f_cfg}": "p+f",
        "2d52_1g92": "d+g",
    }

    # remove any None placeholders (in case f_cfg is missing)
    panel_order = [p for p in panel_order if p is not None]


    singles = ["2p32", "2d52", "1g92"]
    if f_cfg:
        singles.insert(2, f_cfg)  # keep f in the same visual position

    mixed_pairs = [("2d52", "1g92")]
    if f_cfg:
        mixed_pairs.insert(0, ("2p32", f_cfg))

    jobs = []
    for cfg in singles:
        if cfg in cfg_map:
            jobs.append(([cfg_map[cfg]], cfg))
        else:
            print(f"WARNING: missing theory file for config {cfg} at {energy} keV")

    for a, b in mixed_pairs:
        if a in cfg_map and b in cfg_map:
            jobs.append(([cfg_map[a], cfg_map[b]], f"{a}+{b}"))
        else:
            print(f"WARNING: missing theory file for mixed {a}+{b} at {energy} keV")

    if not jobs:
        raise RuntimeError("No fit jobs could be constructed (no matching theory files).")

    # --------- make the 2x3 grid figure ----------
    fig, axes = plt.subplots(2, 3, figsize=(11, 7), sharex=True, sharey=True)
    fig.suptitle(
    rf"${energy}\ \mathrm{{keV}}$",
    fontsize=12,
    y=0.98
    )
    axes = axes.flatten()
    ax_map = {k: axes[i] for i, k in enumerate(panel_order)}

    # Suppress any accidental plt.show() inside old codepaths
    orig_show = plt.show
    plt.show = lambda *a, **k: None

    cwd0 = os.getcwd()
    results_summary = []

    try:
        os.chdir(base)
        cross_section_file, cross_sec_path = merge.get_cross_section(base, energy)

        # remove old .inp files for this energy
        for f in os.listdir(minimizing_dir):
            if f.startswith(f"48Ti_{energy}_") and f.endswith(".inp"):
                os.remove(os.path.join(minimizing_dir, f))

        # generate .inp files
        # Worked for 8.6kG, changing to correctly get the _7.6kG files
        # for fresco_files, _label in jobs:
        #     merge.write_to_file(base, cross_sec_path, fresco_dir, cross_section_file, fresco_files)
        #     inp_name = inp_name_for_files(fresco_files)
        #     inp_path = os.path.join(minimizing_dir, inp_name)
        #     if not os.path.isfile(inp_path):
        #         raise FileNotFoundError(f"Expected .inp not found after merge: {inp_path}")
        for fresco_files, _label in jobs:
            # find the .inp file that merge just wrote
            merge.write_to_file(base, cross_sec_path, fresco_dir, cross_section_file, fresco_files)
            energy_tag = f"{energy}"
            matches = [
                f for f in os.listdir(minimizing_dir)
                if f.endswith(".inp")
                and energy_tag in f
                and all(cfg in f for cfg in [os.path.splitext(x)[0].split("_")[2] for x in fresco_files])
            ]

            if len(matches) != 1:
                raise FileNotFoundError(
                    f"Could not uniquely identify .inp after merge. Found: {matches}"
                )

            inp_path = os.path.join(minimizing_dir, matches[0])


        # fit the 6 .inp files
        inp_files = sorted(
            f for f in glob.glob(os.path.join(minimizing_dir, "*.inp"))
            if f.startswith(os.path.join(minimizing_dir, f"48Ti_{energy}_"))
        )

        print(f"\nFitting {len(inp_files)} .inp files...")

        for inp in inp_files:
            key = panel_key_from_inp(inp)
            ax = ax_map.get(key, None)
            lbl = panel_labels.get(key, key)
            fitres = run_fit_on_inp(inp, ax=ax, panel_label=lbl)
            results_summary.append(fitres)

    finally:
        plt.show = orig_show
        os.chdir(cwd0)

    # shared labels + tidy axes
    fig.supxlabel(r'$\Theta_{CM}$ [deg]')
    fig.supylabel(r'd$\sigma$/d$\Omega$ [mb/sr]')
    fig.tight_layout()

    # print compact summary
    print("\n================ SUMMARY ================")
    results_summary = sorted(results_summary, key=lambda r: r["redchi"])
    for r in results_summary:
        if not r["mixed"]:
            sf, sferr = r["params"]["SF"]
            sf_fmt = sig_round(sf, sferr, style="Drake", sep="external_brackets", spacer="")
            print(
                f"{r['label']}:  "
                f"SF={sf_fmt}   "
                f"redchi={r['redchi']:.3f}"
            )
        else:
            sf1, e1 = r["params"]["SF1"]
            sf2, e2 = r["params"]["SF2"]
            sf1_fmt = sig_round(sf1, e1, style="Drake", sep="external_brackets", spacer="")
            sf2_fmt = sig_round(sf2, e2, style="Drake", sep="external_brackets", spacer="")
            print(
                f"{r['label']}:  "
                f"SF1={sf1_fmt}  "
                f"SF2={sf2_fmt}   "
                f"redchi={r['redchi']:.3f}"
            )
    print("=========================================\n")
    def format_sf_single(sf, sferr):
        # e.g. 0.014(2)
        return sig_round(sf, sferr, style="Drake", sep="external_brackets", spacer="")

    def format_sf_mixed(sf1, e1, sf2, e2):
        # e.g. 0.05(1)+0.16(3)
        a = sig_round(sf1, e1, style="Drake", sep="external_brackets", spacer="")
        b = sig_round(sf2, e2, style="Drake", sep="external_brackets", spacer="")
        return f"{a}+{b}"


    # ----- choose best fit (lowest chi-square) -----
    best = min(results_summary, key=lambda r: r["redchi"])

    inp_label = best["label"]  # filename like 48Ti_5158_2p32_4+_7.6kG.inp
    cfgs, J = parse_inp_for_cfgs_and_J(inp_label)

    L_transfer = cfgs_to_L_transfer(cfgs)
    orbit_cfg = cfgs_to_orbit_string(cfgs)

    # SF formatting
    if not best["mixed"]:
        sf, sferr = best["params"]["SF"]
        sf_str = format_sf_single(sf, sferr)
    else:
        sf1, e1 = best["params"]["SF1"]
        sf2, e2 = best["params"]["SF2"]
        sf_str = format_sf_mixed(sf1, e1, sf2, e2)

    chisq_str = f"{best['redchi']:.3f}"  # matches your file style pretty closely

    # ----- pick output file name based on your suffix convention -----
    # If you pass suffix like "_7.6kG", use that, otherwise default to "8.6kG" or blank.
    # Simplest: infer suffix from the inp name:
    suffix = ""
    m = re.search(r"_(\d+\.\d+kG)$", inp_label.replace(".inp", ""))
    if m:
        print(f"Using suffix from inp name: _{m.group(1)}")
        suffix = "_" + m.group(1)

    out_name = f"SF_strength{suffix}.txt"
    out_path = os.path.join(base, out_name)

    # ----- append line (create file with header if missing) -----
    need_header = (not os.path.exists(out_path)) or (os.path.getsize(out_path) == 0)

    with open(out_path, "a") as f:
        if need_header:
            f.write("Energy\tL transfer\tOrbital Config\tJ state\tSF\tChi-sq\n")
        print({"energy": energy, "L_transfer": L_transfer, "orbit_cfg": orbit_cfg, "J": J, "sf_str": sf_str, "chisq_str": chisq_str})
        f.write(f"{energy}\t{L_transfer}\t{orbit_cfg}\t{J if J is not None else ''}\t{sf_str}\t{chisq_str}\n")

    print(f"Wrote best-fit strength row to: {out_path}")

    # show the single combined figure
    out_img_dir = os.path.join(base, "fit_slides")
    os.makedirs(out_img_dir, exist_ok=True)

    img_path = os.path.join(out_img_dir, f"{energy}_keV.png")
    fig.savefig(img_path, dpi=300, bbox_inches="tight")
    print(f"Saved slide image: {img_path}") 
    plt.show()


if __name__ == "__main__":
    main()
