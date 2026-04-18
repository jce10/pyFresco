import os
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
import fnmatch
from lmfit import Model, Parameters
from sigfig import round


#lab_angles = [15,20,25,30,35,40,45,50]
tex_fonts = {
                # Use LaTeX to write all text
                # "text.usetex": True,
                "font.family": "serif",
                "font.serif": "Computer Modern Roman",
    # Use 10pt font in plots, to match 10pt font in document
    "axes.labelsize": 7,
    "font.size": 6,
    # Make the legend/label fonts a little smaller
    "legend.fontsize": 7,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    # Use CMR for math fonts (requires LaTeX)
    "mathtext.fontset": "cm",
    }

fresco_output_path = '/home/bkelly/Programs/chi_squared_fitting/fresco_output_files'

def custom_sort_key(file_name):
    order = {}
    for char in 'spdfg':
        order[char] = file_name.find(char) if char in file_name else float('inf')
    return [order[char] for char in 'spdfg']

def sort_lists(list1, list2):
    return [x for _, x in sorted(zip(list2, list1))]

def ADWA_Fit(x,SF):
    return SF*x

def ADWA_Mixed_Fit(x, SF1, SF2):
    return SF1*x[0] + SF2*x[1]


def plot_data(
    MIXED_STRENGTH,
    result,
    lab_angles,
    x_sec_vals,
    error_vals,
    fresco_vals,
    energy,
    inp_name=None,
    ax=None,
    panel_label=None
):
    os.chdir(fresco_output_path)
    totalFiles = os.listdir(fresco_output_path)

    # Decide whether we are plotting into an existing grid axis or standalone
    standalone = (ax is None)
    if standalone:
        fig_local, ax = plt.subplots(figsize=(5.5, 4.2))

    # Common y-limits (based on data)
    min_y = float(np.min(x_sec_vals))
    max_y = float(np.max(x_sec_vals))
    ylo, yhi = min_y / 10.0, max_y * 10.0

    # Helper: draw panel label
    if panel_label is not None:
        ax.text(
            0.05, 0.95, panel_label,
            transform=ax.transAxes,
            ha="left", va="top"
        )

    if MIXED_STRENGTH is False:
        # ---- SINGLE ----
        if inp_name is None:
            print("ERROR: plot_data() called without inp_name")
            return

        inp_file = os.path.basename(inp_name)
        tokens = inp_file.replace(".inp", "").split("_")

        try:
            config = next(t for t in tokens if any(c in t for c in ["p", "d", "f", "g"]))
        except StopIteration:
            print(f"ERROR: could not infer l-config from inp file: {inp_file}")
            return

        e_tag = f"_{energy}_"

        try:
            sorted_file = next(
                f for f in totalFiles
                if f.endswith(".sorted") and (e_tag in f) and (config in f)
            )
        except StopIteration:
            print(f"No matching .sorted file for {energy} keV with config {config}")
            return

        data = np.loadtxt(sorted_file)
        x = data[:, 0]
        y = data[:, 1]

        SF = result.params["SF"].value
        std_err = result.params["SF"].stderr

        formatted_result = round(SF, std_err, style="Drake", sep="external_brackets", spacer="")
        print("Unrounded SF w/ error: ", f"{SF:.5f}({std_err:.5f})")
        print(f"SF w/ error: {formatted_result}")
        print(f"Reduced chi-square value of: {result.redchi:.3f}")

        scaled_y = y * SF
        lowbound = y * (SF - std_err)
        upperbound = y * (SF + std_err)

        ax.plot(x, scaled_y, linestyle="--", color="darkblue", label="Scaled ADWA", alpha=1.0)
        ax.fill_between(x, lowbound, upperbound, color="grey", alpha=0.5, label="Std. Dev.")
        ax.errorbar(
            lab_angles, x_sec_vals, yerr=error_vals,
            color="black", marker="x", linestyle="None",
            ecolor="red", capsize=2, label="Experimental data"
        )

        ax.set_yscale("log")
        ax.set_ylim(ylo, yhi)
        ax.minorticks_on()
        ax.tick_params(which="major", length=6, direction="in", top=True, right=True, left=True, bottom=True)
        ax.tick_params(which="minor", length=4, direction="in", top=True, right=True, left=True, bottom=True)
        chi2_text = rf"$\chi^2_\nu = {result.redchi:.2f}$"


        ax.text(
            0.20, 0.95,
            rf"$S = {formatted_result}$",
            transform=ax.transAxes,
            fontsize=9,
            verticalalignment="top"
        )
        ax.text(
            0.20, 0.85,
            chi2_text,
            transform=ax.transAxes,
            fontsize=9,
            verticalalignment="top",
            horizontalalignment="left",
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.85),
        )

        # Only add labels/legend in standalone mode (grid will use shared labels)
        if standalone:
            ax.set_xlabel(r"$\Theta_{CM}$ [deg]")
            ax.set_ylabel(r"d$\sigma$/d$\Omega$ [mb/sr]")
            ax.legend(frameon=False)
            plt.tight_layout()
            plt.show()

    else:
        # ---- MIXED ----
        if inp_name is None:
            print("ERROR: plot_data() called without inp_name (mixed fit)")
            return

        inp_file = os.path.basename(inp_name)
        tokens = inp_file.replace(".inp", "").split("_")
        configs = [t for t in tokens if any(c in t for c in ["p", "d", "f", "g"])]

        if len(configs) != 2:
            print(f"ERROR: mixed fit inp does not contain 2 configs: {inp_file}")
            return

        matching_files = []
        for cfg in configs:
            for f in totalFiles:
                e_tag = f"_{energy}_"
                if f.endswith(".sorted") and (cfg in f) and (e_tag in f):
                    matching_files.append(f)

        matching_files = sorted(set(matching_files))
        if len(matching_files) != 2:
            print(f"Expected 2 mixed configs, found {len(matching_files)}: {matching_files}")
            return

        SF1 = result.params["SF1"].value
        std_err_1 = result.params["SF1"].stderr
        SF2 = result.params["SF2"].value
        std_err_2 = result.params["SF2"].stderr

        formatted_result1 = round(SF1, std_err_1, style="Drake", sep="external_brackets", spacer="")
        formatted_result2 = round(SF2, std_err_2, style="Drake", sep="external_brackets", spacer="")
        print(f"Low  l-transfer SF w/ error: {formatted_result1}")
        print(f"High l-transfer SF w/ error: {formatted_result2}")
        print(f"Reduced chi-square value of: {result.redchi:.3f}")
        print("Pulled from files: ", matching_files)

        # Ensure low-l config plotted first (your original logic)
        cfgs_for_sort = []
        for file in matching_files:
            cfgs_for_sort.append(file.split("_")[2])
        sorted_cfgs = sorted(cfgs_for_sort, key=custom_sort_key)
        sorted_list1 = sort_lists(matching_files, sorted_cfgs)

        data0 = np.loadtxt(sorted_list1[0])
        x0 = data0[:, 0]
        y0 = data0[:, 1]

        data1 = np.loadtxt(sorted_list1[1])
        x1 = data1[:, 0]
        y1 = data1[:, 1]

        y0_scaled = SF1 * y0
        y1_scaled = SF2 * y1

        ax.plot(x0, y0_scaled, linestyle="--", color="dodgerblue", label="Low-l config")
        ax.fill_between(x0, y0 * (SF1 - std_err_1), y0 * (SF1 + std_err_1), color="dodgerblue", alpha=0.2)

        ax.plot(x1, y1_scaled, linestyle="--", color="magenta", label="High-l config")
        ax.fill_between(x1, y1 * (SF2 - std_err_2), y1 * (SF2 + std_err_2), color="magenta", alpha=0.2)

        adwa_curve = y0_scaled + y1_scaled
        adwa_curve_lowbound = y0 * (SF1 - std_err_1) + y1 * (SF2 - std_err_2)
        adwa_curve_upperbound = y0 * (SF1 + std_err_1) + y1 * (SF2 + std_err_2)

        ax.plot(x0, adwa_curve, linestyle="--", color="darkblue", label="Scaled ADWA", alpha=1.0)
        ax.fill_between(x0, adwa_curve_lowbound, adwa_curve_upperbound, color="grey", alpha=0.5, label="Std. Dev.")

        ax.errorbar(
            lab_angles, x_sec_vals, yerr=error_vals,
            color="black", marker="x", linestyle="None",
            ecolor="red", capsize=2, label="Experimental data"
        )

        ax.set_yscale("log")
        ax.set_ylim(ylo, yhi)
        ax.minorticks_on()
        ax.tick_params(which="major", length=6, direction="in", top=True, right=True, left=True, bottom=True)
        ax.tick_params(which="minor", length=4, direction="in", top=True, right=True, left=True, bottom=True)
        chi2_text = rf"$\chi^2_\nu = {result.redchi:.2f}$"


        ax.text(
                0.20, 0.95,
                rf"$S_1 = {formatted_result1}$",
                transform=ax.transAxes,
                fontsize=9,
                verticalalignment="top")

        ax.text(
                0.6, 0.95,
                rf"$S_2 = {formatted_result2}$",
                transform=ax.transAxes,
                fontsize=9,
                verticalalignment="top"
                )
        ax.text(
            0.20, 0.85,
            chi2_text,
            transform=ax.transAxes,
            fontsize=9,
            verticalalignment="top",
            horizontalalignment="left",
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.85),
        )
        if standalone:
            ax.set_xlabel(r"$\Theta_{CM}$ [deg]")
            ax.set_ylabel(r"d$\sigma$/d$\Omega$ [mb/sr]")
            ax.legend(frameon=False)
            plt.tight_layout()
            plt.show()

def main():
    dir = os.getcwd()
    minimizing_folder = f'{dir}/minimizing_folder'
    sorted_files = sorted(os.listdir(minimizing_folder))
    MIXED_STRENGTH = None
    for file in sorted_files:
        if os.path.isdir(file):
            continue
        energy = file.split('_')[1]
        print(f"Starting Chi-Squared for {energy} keV state from file: {file}")
        data = np.loadtxt(f'{minimizing_folder}/{file}')
        if data.shape[1] == 4:
            MIXED_STRENGTH = False
            angles, x_sec_vals, error_vals, fresco_vals = np.transpose(data)
            valid_mask = (x_sec_vals > 0) & (error_vals > 0) & ~np.isnan(x_sec_vals) & ~np.isnan(error_vals)
            angles = angles[valid_mask]
            x_sec_vals = x_sec_vals[valid_mask]
            error_vals = error_vals[valid_mask]
            fresco_vals = fresco_vals[valid_mask]
            fresco = np.asarray(fresco_vals)
            model = Model(ADWA_Fit)
            params = Parameters()
            params.add('SF', value=0.1)
            result = model.fit(x_sec_vals, x=fresco, params=params, weights= 1.0/error_vals)
            optimized_params = result.params
            # print(optimized_params)
            plot_data(MIXED_STRENGTH, result, angles, x_sec_vals, error_vals, fresco_vals, energy, inp_name=file)
            print('\n')
        else:
            MIXED_STRENGTH = True
            angles, x_sec_vals, error_vals, fresco_vals1, fresco_vals2 = np.transpose(data)
            valid_mask = (x_sec_vals > 0) & (error_vals > 0) & ~np.isnan(x_sec_vals) & ~np.isnan(error_vals)
            angles = angles[valid_mask]
            x_sec_vals = x_sec_vals[valid_mask]
            error_vals = error_vals[valid_mask]
            fresco_vals1 = fresco_vals1[valid_mask]
            fresco_vals2 = fresco_vals2[valid_mask]
            combined_fresco_arr = np.array([fresco_vals1, fresco_vals2])
            model = Model(ADWA_Mixed_Fit)
            params = Parameters()
            params.add('SF1', 0.5, min=0.0001, max=1.0)
            params.add('SF2', 0.5, min=0.0001, max=1.0)
            result = model.fit(x_sec_vals, x=combined_fresco_arr, params=params, weights=1.0/error_vals)
            optimized_params = result.params
            # print(optimized_params)            
            plot_data(MIXED_STRENGTH, result, angles, x_sec_vals, error_vals, combined_fresco_arr, energy, inp_name=file)
            print('\n')



if __name__ == '__main__':
    main()
