import re
from pathlib import Path

from pyfresco.fresco_runner import run_fresco
from pyfresco.card_builders.adwa import build_adwa_input
from pyfresco.card_builders.dwba import build_dwba_input

"""
    This handles the creation of the input file for FRESCO.
    The input file is created based on the parameters in the reaction_config.json file, and uses the ADWA_potentials.py file to
    calculate the deuteron and proton potentials.

    Make sure that you updated the path to the FRESCO executable file in the reaction_config.json.

    DO NOT ADJUST SPACING, the f-string below looks crazy with all parameters filled but the formatting is very particular 
"""

l_dict = {'s': 0, 'p': 1, 'd': 2, 'f': 3, 'g': 4, 'h': 5, 'i': 6, 'j': 7}
frac_dict = {'0.5': 12, '1.5': 32, '2.5': 52, '3.5': 72, '4.5': 92, '5.5': 112, '6.5': 132, '7.5': 152}

CARD_BUILDERS = {
    "adwa": build_adwa_input,
    "dwba": build_dwba_input,
}


def create_input_files(
    energies,
    ns,
    ls,
    js_transfer,
    js_finalstate,
    deuteron_pot,
    proton_pot,
    config,
):
    # check which approximation method is being used and select the appropriate input card builder function
    approx = config["approx"].strip().lower()
    
    # create the output directory
    output_root_dir = Path(config["output_root_dir"]).expanduser()
    output_root_dir.mkdir(parents=True, exist_ok=True)

    # read in rxn values from config
    Z_fmt = f"{config['Z']:4.1f}"
    mass_in = f"{config['mass_in']:7.3f}"
    mass_out = f"{config['mass_out']:7.3f}"
    gs_spin_fmt = f"{config['gs_spin']:4.1f}"
    gs_parity_fmt = f"{config['gs_parity']:>2}"
    th_min = f"{config['angle_min']:4.1f}"
    th_max = f"{config['angle_max']:4.1f}"
    th_step = f"{config['angle_step']:3.1f}"

    at = float(config['AT'])
    residual_mass = float(config['residual_mass'])

    match = re.match(r"(\d+)([A-Za-z]+)", config["label_out"])
    mass, element = match.groups()
    label_out_reversed = element.lower() + mass

    even_mass_final = int(config["label_out"][0:2]) % 2 == 0

    # added a dictionary to pass as variables to the input card builders, 
    # to avoid having to pass the entire config file and state dictionary
    shared = {
    "Z_fmt": Z_fmt,
    "mass_in": mass_in,
    "mass_out": mass_out,
    "gs_spin_fmt": gs_spin_fmt,
    "gs_parity_fmt": gs_parity_fmt,
    "th_min": th_min,
    "th_max": th_max,
    "th_step": th_step,
    "at": at,
    "residual_mass": residual_mass,
    "label_out_reversed": label_out_reversed,
    }

    for i in range(len(energies)):
        q = f"{config['Q_value']:6.4f}"
        e = f"{energies[i]:5.3f}"
        be = f"{(config['binding_energy'] - float(e)):6.4f}"
        energy_keV = int(round(float(e) * 1000))
        l = l_dict[ls[i]]

        if l % 2 == 0:
            final_parity = config["gs_parity"]
        else:
            final_parity = "+1" if config["gs_parity"] == "-1" else "-1"

        transfer_info = {
            "energy": energy_keV,
            "n": ns[i],
            "l": ls[i],
            "js_transfer": frac_dict[js_transfer[i]],
            "js_final": js_finalstate[i],
            "js_final_fmt": frac_dict.get(str(js_finalstate[i]), str(js_finalstate[i])),
            "parity": final_parity[0],
        }

        if even_mass_final:
            string_suffix = (
                f"{transfer_info['energy']}_{transfer_info['n']}"
                f"{transfer_info['l']}{transfer_info['js_transfer']}_"
                f"{int(transfer_info['js_final'])}{transfer_info['parity']}"
            )
        else:
            string_suffix = (
                f"{transfer_info['energy']}_{transfer_info['n']}"
                f"{transfer_info['l']}{transfer_info['js_transfer']}_"
                f"{frac_dict[str(transfer_info['js_final'])]}{transfer_info['parity']}"
            )
        
        state = {
            "q": q,
            "e": e,
            "be": be,
            "energy_keV": energy_keV,
            "n": ns[i],
            "l_letter": ls[i],
            "l_value": l,
            "js_transfer": js_transfer[i],
            "js_finalstate": js_finalstate[i],
            "final_parity": final_parity,
            "string_suffix": string_suffix,
        }


        # handling the organization of the output FRESCO directories
        if energy_keV == 0:
            ex_dirname = "GS"
        else:
            ex_dirname = f"{energy_keV}keV"

        run_dir = output_root_dir / ex_dirname / approx / string_suffix
        run_dir.mkdir(parents=True, exist_ok=True)


        # make FRESCO input card based on which approximation method is being used
        if approx == "adwa":
            fri = build_adwa_input(
                shared=shared,
                state=state,
                deuteron_pot=deuteron_pot,
                proton_pot=proton_pot,
                config=config,
            )
        elif approx == "dwba":
            fri = build_dwba_input(
                shared=shared,
                state=state,
                deuteron_pot=deuteron_pot,
                proton_pot=proton_pot,
                config=config,
            )
        else:
            raise ValueError(f"Unknown approximation method: {approx!r}")

        infile = run_dir / f"{label_out_reversed}dp_{approx}_{string_suffix}.fri"
        outfile = run_dir / f"{label_out_reversed}dp_{approx}_{string_suffix}.fro"

        with open(infile, "w") as file:
            file.write(fri)

        run_fresco(
            infile=infile.name,
            outfile=outfile.name,
            run_dir=run_dir,
            string_suffix=string_suffix,
            transfer_info=transfer_info,
            even_mass_final=even_mass_final,
            config=config,
        )



# I WANT TO ADD A MORE GENERAL WAY TO CALL THE CARD BUILDERS, but I am not sure how to handle the different arguments that they require.
# try:
#     builder = CARD_BUILDERS[approx]
# except KeyError:
#     raise ValueError(
#         f"Unsupported approximation {approx!r}. "
#         f"Supported: {', '.join(CARD_BUILDERS)}"
#     )
