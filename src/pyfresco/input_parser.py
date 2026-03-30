from pyfresco.config import INPUT_GENERATOR_FILE

"""

This module scrapes the input_generator.inp file for the energies, jpi, and transfer configuration
and returns them in a list. More than one state can be calculated at once, so however many
states are given in input_generator.inp will be calculated, and fresco will be ran for each of them.

"""
def get_input(input_path=INPUT_GENERATOR_FILE):
    energies = []
    ns = []
    ls = []
    js_transfer = []
    js_finalstate = []

    with open(input_path, "r") as input_file:
        for line in input_file:
            stripped = line.strip()

            if not stripped:
                continue
            if stripped.startswith("#"):
                continue

            args = stripped.split()
            energies.append(float(args[0]))
            js_finalstate.append(float(args[1]))
            ns.append(args[2])
            ls.append(args[3])
            js_transfer.append(args[4])

    return energies, ns, ls, js_transfer, js_finalstate