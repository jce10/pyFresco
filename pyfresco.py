import os
import subprocess
import textwrap
import json
from pathlib import Path
import ADWA_potentials as adwa_pot

# base_title = '50Ti(d,p)51Ti 16 MeV (ADWA)'
# binding    = 6.3725 # neutron separation energy of final nucleus in MeV
# Qvalue     = 4.1479 # Q-value of the reaction in MeV
# Z          = 22
# label_in   = '50Ti' # 4 characters
# m_in    = 49.9447
# label_out  = '51Ti' # 4 characters
# m_out   = 50.9466
# gs_spin = 0.0
# gs_parity = '+1'

# Dictionaries used for formatting and parity assignment logic
l_dict = {'s': 0, 'p': 1, 'd': 2, 'f': 3, 'g': 4, 'h': 5, 'i': 6, 'j': 7}
frac_dict = {'0.5': 12, '1.5': 32, '2.5': 52, '3.5': 72, '4.5': 92, '5.5': 112, '6.5': 132, '7.5': 152} 

    


def load_reaction_config(config_path):
    """
    Loads the reaction configuration from a JSON file.

    Parameters:
    - config_path (str or Path): Path to the JSON config file.

    Returns:
    - dict: A dictionary containing all reaction parameters.
    """
    config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, "r") as file:
        config = json.load(file)

    return config
    
def getInput():
    inputFileName = 'input_generator.inp'
    inputFile = open(inputFileName, 'r')
    energies = []
    ns       = []
    ls       = []
    js_transfer = []
    js_finalstate = []
    while True:
        line = inputFile.readline()
        if line.startswith('#'):
            continue
        if line == '':
            break
        args = line.split()
        energies.append(float(args[0]))
        js_finalstate.append(float(args[1]))
        ns.append(args[2])
        ls.append(args[3])
        js_transfer.append(args[4])
    
    return energies, ns, ls, js_transfer, js_finalstate

def runFresco(inFile, outfile, dir, string_suffix, transfer_info, evenMassFinal, config):
    # Run the FRESCO executable with the input file
    executable_path = './bin/fresco'
    command_string = f'{executable_path} < {inFile} > {outfile}'
    command = [command_string] 
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as error:
        print(f'Error running the command {error}')
    
    # take the cross-section output file & rename it so it does not get overwritten in the next iteration
    x_sec_outfile = f'{dir}/fort.16'
    renamed_outfile = f"{dir}/{config['label_out']}_{string_suffix}.txt"

    try:
        os.rename(x_sec_outfile, renamed_outfile)
        print(f"File '{x_sec_outfile}' has been renamed to '{renamed_outfile}'.")
    except FileNotFoundError:
        print(f"Error: File '{x_sec_outfile}' not found.")
    except FileExistsError:
        print(f"Error: File '{renamed_outfile}' already exists.")
    except Exception as error:
        print(f"An error occurred: {error}")
    if evenMassFinal:
        print(f'Calculated the transfer to the Jpi={int(transfer_info["js_final"])}{transfer_info["parity"]}, {transfer_info["n"]}{transfer_info["l"]}{transfer_info["js_transfer"]} configuration')
    else:
        print(f'Calculated the transfer to the Jpi={frac_dict[str(transfer_info["js_final"])]}{transfer_info["parity"]}, {transfer_info["n"]}{transfer_info["l"]}{transfer_info["js_transfer"]} configuration')
    print(f"Successfully ran fresco & created cross-section file {renamed_outfile}")

def createInputFile(energies, ns, ls, js_transfer, js_finalstate, deuteron_pot, proton_pot, config):
    """
    Below is an example of a default fresco input file, where the main things that changes
    from one input file to another are the energy, the l transfer, the jpi, and the parity.

    Therefore, this changes the corresponding lines in the input file, and generates a unique input file 
    for each of the different configurations.

    DO NOT ADJUST SPACING, just optical model values need to be change from reaction to reaction -- otherwise spacing is very sensitive 
    """

    # Loop through each line in the input file, create file and then run FRESCO to get output
    Z_fmt = f"{config['Z']:4.1f}"
    mass_in = f"{config['mass_in']:7.4f}"
    mass_out = f"{config['mass_out']:7.4f}"
    gs_spin_fmt = f"{config['gs_spin']:4.1f}"     # Ensures correct spacing and decimal format
    gs_parity_fmt = f"{config['gs_parity']:>2}"
    label_out_reversed = config['label_out'][-2:].lower() + config['label_out'][:-2]

    # lines = fri.strip().split('\n')
    # target_line = lines[7]  # Get the line with the ground state spin + parity
    # tokens = target_line.split()
    # ground_state_parity = tokens[-2] # Get the parity value, used for assigning parity to the final state given an angular momentum transfer
    evenMassFinal = True if int(config['label_out'][0:2]) % 2 == 0 else False
    
    for i in range(len(energies)):
        
        q = f"{config['Q_value']:6.4f}"
        e =  f"{energies[i]:5.3f}"
        be = f"{(config['binding_energy'] - float(e)):6.4f}"
        energy = float(e) * 1000
        l = l_dict[ls[i]]
        if l % 2 == 0:
            final_parity = config['gs_parity']
        else:
            final_parity = '+1' if config['gs_parity'] == '-1' else '-1'
        transfer_info = {
            'energy': int(energy),
            'n': ns[i],
            'l': ls[i],
            'js_transfer': frac_dict[js_transfer[i]],
            'js_final': js_finalstate[i],
            'parity': final_parity[0],  # e.g., '+' or '-'
        }

        fri=f'''{config['reaction']}, {js_finalstate[i]}{final_parity[0]} {e} MeV {ns[i]}{ls[i]}{js_transfer[i]}
0.10    55.0    0.20    0.20    30.0    -6.0
 00. 20.  +.00   F F
0  15.0     65.   0.1  1
0.0    0 1   1 1  48          .000    0.   0.001
 1 1 0 0 2 3 0 0-3 1 0 0 1
2H      2.0141  1.0        1  {config['label_in']}    {mass_in} {float(config['Z'])}    0.0000
1.0   +1 0.0               1 {gs_spin_fmt}   {gs_parity_fmt} 0.000
1H      1.0078  1.0        1  {config['label_out']}    {mass_out} {float(config['Z'])}    {q}
0.5   +1 0.0               2  {js_finalstate[i]}   {final_parity} {e}

  1 0  0    50.0     0.0   1.269
  1 1  0   {deuteron_pot['V']:5.2f}   {deuteron_pot['r0']:5.3f}   {deuteron_pot['a']:5.3f}   {deuteron_pot['Vi']:5.3f}   {deuteron_pot['ri0']:5.3f}   {deuteron_pot['ai']:5.3f}
  1 2  0                           {deuteron_pot['Vsi']:5.2f}   {deuteron_pot['rsi0']:5.3f}   {deuteron_pot['asi']:5.3f}
  1 3  0   {deuteron_pot['Vso']:5.2f}   {deuteron_pot['rso0']:5.3f}   {deuteron_pot['aso']:5.3f}   {deuteron_pot['Vsoi']:5.2f}   {deuteron_pot['rsoi0']:5.3f}   {deuteron_pot['asoi']:5.3f}
  2 0  0    51.0     0.0   1.267
  2 1  0   {proton_pot['V']:5.2f}   {proton_pot['r0']:5.3f}   {proton_pot['a']:5.3f}   {proton_pot['Vi']:5.3f}   {proton_pot['ri0']:5.3f}   {proton_pot['ai']:5.3f}
  2 2  0                           {proton_pot['Vsi']:5.2f}   {proton_pot['rsi0']:5.3f}   {proton_pot['asi']:5.3f}
  2 3  0   {proton_pot['Vso']:5.2f}   {proton_pot['rso0']:5.3f}   {proton_pot['aso']:5.3f}   {proton_pot['Vsoi']:5.2f}   {proton_pot['rsoi0']:5.3f}   {proton_pot['asoi']:5.3f}
  3 0  0    1.00            1.25
  3 1  5    1.00            1.00
  3 3  5    1.00            1.00
  3 4  5    1.00            1.00
  3 7  5    1.00            1.00
  4 0  0    51.0     0.0    1.25
  4 1  0    50.0    1.25    0.65
  4 3  0     6.0    1.25    0.65
0
  1  2 1 2-1 3   1 0 2 0.5 1 1.5 1  3  0  2.2260  0  3  0
  3    1 2-2 0   {ns[i]} {l}   0.5   {js_transfer[i]}    4  0  {be}  1  0  0

  -2   1   7 0-1 0
       1   1   1   1  1.0000
       2   1   1   3  1.0000
0
   0   1   1
16.0
EOF
'''

        if evenMassFinal: # landing on even nucleus
            string_suffix = f'{transfer_info["energy"]}_{transfer_info["n"]}{transfer_info["l"]}{transfer_info["js_transfer"]}_{int(transfer_info["js_final"])}{transfer_info["parity"]}'
            fileName = f'{label_out_reversed}dp_adwa_{string_suffix}.fri'
            inFile = fileName
            outfile = f'{label_out_reversed}dp_adwa_{string_suffix}.fro'
        else:
            string_suffix = f'{transfer_info["energy"]}_{transfer_info["n"]}{transfer_info["l"]}{transfer_info["js_transfer"]}_{frac_dict[str(transfer_info["js_final"])]}{transfer_info["parity"]}'
            fileName = f'{label_out_reversed}dp_adwa_{string_suffix}.fri'
            inFile = fileName
            outfile = f'{label_out_reversed}dp_adwa_{string_suffix}.fro'
        if not os.path.exists(inFile):
            with open(inFile, 'w') as file:
                file.write(fri)
        runFresco(inFile, outfile, os.getcwd(), string_suffix, transfer_info, evenMassFinal, config)

        
def main():
    config = load_reaction_config("reaction_config.json")
    beam_energy, zt, at = config["beam_energy"], config["Z"], config["AT"]
    # print(beam_energy, zt, at)
    residual_mass = float(at) + 1
    deuteron_pot = adwa_pot.Wales_Johnson_deutron_AWDA(beam_energy, zt, at)
    proton_pot = adwa_pot.koning_delaroche_proton_potential(beam_energy, zt, residual_mass)
    energies, ns, ls, js_transfer, js_finalstate = getInput()
    createInputFile(energies, ns, ls, js_transfer, js_finalstate, deuteron_pot, proton_pot, config)
    

if __name__ == "__main__":
    main()

