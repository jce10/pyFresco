"""
This module runs the FRESCO executable with the given input file and handles the output.
It copies the fort.16 file so the original stays in place, then uses the copy for further processing.

Make sure to adjust the path to the FRESCO executable in the reaction_config file.

The fort.16 file is where the inelastic channel cross-section is stored.

A fresco .fri (input) and .fro (output) file, and {nucleus}_{energy}_{n}{l}{jpi}.txt (cross-section output) file is created for each state.
The inelastic channel is the second partition, the elastic is always calculated and is the first set of cross-section data.
"""

import subprocess
import shutil
from pathlib import Path
from rich.console import Console

from pyfresco.output_parser import write_sorted_from_fresco_output

console = Console()

def run_fresco(infile, outfile, run_dir, string_suffix, transfer_info, even_mass_final, config):
    
    # alias for nested sections in the config file
    reaction = config["reaction"]
    runtime = config["runtime"]
    
    run_dir = Path(run_dir)
    executable_path = runtime["executable_path"]
    approx = reaction["approx"].strip().lower()

    # print each time FRESCO is run, to keep track of progress
    console.print(f"\n\t[blue]fresco< '{infile}' > '{outfile}'[/]\n")
    command_string = f"{executable_path} < {infile} > {outfile}"

    try:
        subprocess.run(
            command_string,
            shell=True,
            check=True,
            cwd=run_dir
        )
    except subprocess.CalledProcessError as error:
        console.print(f"[red]Error running the command: {error}[/]")
        return

    x_sec_outfile = run_dir / "fort.16"
    renamed_outfile = run_dir / f"{reaction['label_out']}_{approx}_{string_suffix}.txt"

    try:
        shutil.copy2(x_sec_outfile, renamed_outfile)
        console.print(f"[blue]\n\tFresco output file '{x_sec_outfile.name}' has been copied and renamed to '{renamed_outfile.name}'.[/]")

        sorted_basename = f"{reaction['label_out']}_{approx}_{string_suffix}"

        try:
            write_sorted_from_fresco_output(
                infile=str(renamed_outfile),
                out_dir=str(run_dir),
                out_basename=sorted_basename,
            )
        except Exception as e:
            console.print(f"[red]WARNING: failed to write .sorted for {renamed_outfile}: {e}.[/]\n")

    except FileNotFoundError:
        console.print(f"[red]Error: File '{x_sec_outfile}' not found.[/]\n")
    except FileExistsError:
        console.print(f"[red]Error: File '{renamed_outfile}' already exists.[/]\n")
    except Exception as error:
        console.print(f"[red]An error occurred: {error}.[/]\n")

    if even_mass_final:
        console.print(
            f"[blue]\tCalculated the transfer to the "
            f"Jpi={int(transfer_info['js_final'])}{transfer_info['parity']}, "
            f"{transfer_info['n']}{transfer_info['l']}{transfer_info['js_transfer']} configuration.[/]"
        )
    else:
        console.print(
            f"[blue]\tCalculated the transfer to the "
            f"Jpi={transfer_info['js_final_fmt']}{transfer_info['parity']}, "
            f"{transfer_info['n']}{transfer_info['l']}{transfer_info['js_transfer']} configuration.[/]"
        )

    console.print(f"[green]\tSuccessfully ran fresco & created cross-section file {renamed_outfile.name}!\n[/]")