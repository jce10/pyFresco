import subprocess
import shutil
from pathlib import Path

from pyfresco.output_parser import write_sorted_from_fresco_output

"""
This module runs the FRESCO executable with the given input file and handles the output.
It copies the fort.16 file so the original stays in place, then uses the copy for further processing.

Make sure to adjust the path to the FRESCO executable in the reaction_config file.

The fort.16 file is where the inelastic channel cross-section is stored.

A fresco .fri (input) and .fro (output) file, and {nucleus}_{energy}_{n}{l}{jpi}.txt (cross-section output) file is created for each state.
The inelastic channel is the second partition, the elastic is always calculated and is the first set of cross-section data.
"""


def run_fresco(infile, outfile, run_dir, string_suffix, transfer_info, even_mass_final, config):
    run_dir = Path(run_dir)
    executable_path = config["executable_path"]
    approx = config["approx"].strip().lower()

    command_string = f"{executable_path} < {infile} > {outfile}"

    try:
        subprocess.run(
            command_string,
            shell=True,
            check=True,
            cwd=run_dir
        )
    except subprocess.CalledProcessError as error:
        print(f"Error running the command: {error}")
        return

    x_sec_outfile = run_dir / "fort.16"
    renamed_outfile = run_dir / f"{config['label_out']}_{approx}_{string_suffix}.txt"

    try:
        shutil.copy2(x_sec_outfile, renamed_outfile)
        print(f"File '{x_sec_outfile}' has been copied to '{renamed_outfile}'.")

        sorted_basename = f"{config['label_out']}_{approx}_{string_suffix}"
        try:
            write_sorted_from_fresco_output(
                infile=str(renamed_outfile),
                out_dir=str(run_dir),
                out_basename=sorted_basename,
            )
        except Exception as e:
            print(f"WARNING: failed to write .sorted for {renamed_outfile}: {e}")

    except FileNotFoundError:
        print(f"Error: File '{x_sec_outfile}' not found.")
    except FileExistsError:
        print(f"Error: File '{renamed_outfile}' already exists.")
    except Exception as error:
        print(f"An error occurred: {error}")

    if even_mass_final:
        print(
            f"Calculated the transfer to the "
            f"Jpi={int(transfer_info['js_final'])}{transfer_info['parity']}, "
            f"{transfer_info['n']}{transfer_info['l']}{transfer_info['js_transfer']} configuration"
        )
    else:
        print(
            f"Calculated the transfer to the "
            f"Jpi={transfer_info['js_final_fmt']}{transfer_info['parity']}, "
            f"{transfer_info['n']}{transfer_info['l']}{transfer_info['js_transfer']} configuration"
        )

    print(f"Successfully ran fresco & created cross-section file {renamed_outfile}")