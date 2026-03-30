import sys
from pathlib import Path

from pyfresco import omps as adwa_pot

from pyfresco.config import REACTION_CONFIG_FILE
from pyfresco.config_loader import load_reaction_config
from pyfresco.input_parser import get_input
from pyfresco.input_writer import create_input_files

def print_optical_potentials(deuteron_pot, proton_pot, config):
    def _print_block(label, particle, pot):
        print("=" * 60)
        print(f"{label} + {particle} Optical Model Parameters")
        print("=" * 60)

        fmt = "{:<8s} = {:>8.3f}"
        fmtV = "{:<8s} = {:>8.3f}"

        print(fmtV.format("V", pot["V"]))
        print(fmt.format("r0", pot["r0"]))
        print(fmt.format("a", pot["a"]))
        print(fmtV.format("Vi", pot["Vi"]))
        print(fmt.format("ri0", pot["ri0"]))
        print(fmt.format("ai", pot["ai"]))

        print(fmtV.format("Vsi", pot["Vsi"]))
        print(fmt.format("rsi0", pot["rsi0"]))
        print(fmt.format("asi", pot["asi"]))

        print(fmtV.format("Vso", pot["Vso"]))
        print(fmt.format("rso0", pot["rso0"]))
        print(fmt.format("aso", pot["aso"]))
        print(fmtV.format("Vsoi", pot["Vsoi"]))
        print(fmt.format("rsoi0", pot["rsoi0"]))
        print(fmt.format("asoi", pot["asoi"]))

        print(fmt.format("rc0", pot["rc0"]))
        print()

    _print_block(config["label_in"], "d", deuteron_pot)
    _print_block(config["label_out"], "p", proton_pot)


def main(run_dir=None):
    config = load_reaction_config(REACTION_CONFIG_FILE)
    output_root_dir = Path(config["output_root_dir"]).expanduser()
    output_root_dir.mkdir(parents=True, exist_ok=True)

    beam_energy = config["beam_energy"]
    zt = config["Z"]
    at = config["AT"]
    residual_mass = config["residual_mass"]

    deuteron_pot = adwa_pot.Wales_Johnson_deuteron_AWDA(beam_energy, zt, at)
    proton_pot = adwa_pot.koning_delaroche_proton_potential(beam_energy, zt, residual_mass)

    if len(sys.argv) > 1 and sys.argv[1] == "print_params":
        print_optical_potentials(deuteron_pot, proton_pot, config)
        return

    energies, ns, ls, js_transfer, js_finalstate = get_input()

    if run_dir is None:
        run_dir = Path.cwd()

    create_input_files(
        energies,
        ns,
        ls,
        js_transfer,
        js_finalstate,
        deuteron_pot,
        proton_pot,
        config
    )


if __name__ == "__main__":
    main()