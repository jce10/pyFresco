import sys
from pathlib import Path

# from pyfresco import omps
from pyfresco import omps as adwa_pot
from pyfresco import omps as dwba_pot
from pyfresco.config import REACTION_CONFIG_FILE
from pyfresco.config_loader import load_reaction_config
from pyfresco.input_parser import get_input
from pyfresco.input_writer import create_input_files


def print_optical_potentials(entrance_pot, exit_pot, config):
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

    _print_block(config["label_in"], "d", entrance_pot)
    _print_block(config["label_out"], "p", exit_pot)


def main(run_dir=None):
    config = load_reaction_config(REACTION_CONFIG_FILE)
    runtime = config["runtime"]
    reaction = config["reaction"]
    output_root_dir = Path(runtime["output_root_dir"]).expanduser()
    output_root_dir.mkdir(parents=True, exist_ok=True)

    approx = reaction["approx"].strip().lower()
    beam_energy = reaction["beam_energy"]
    zt = reaction["Z"]
    at = reaction["AT"]
    residual_mass = reaction["residual_mass"]

    if approx == "adwa":
        entrance_pot = omps.Wales_Johnson_deuteron_ADWA(beam_energy, zt, at)
        exit_pot =     omps.koning_delaroche_proton_potential(beam_energy, zt, residual_mass)

    elif approx == "dwba":
        entrance_pot = config["potentials"]["dwba"]["entrance"]
        exit_pot = config["potentials"]["dwba"]["exit"]

    elif approx == "ccba":
        raise NotImplementedError("CCBA support not implemented yet.")

    elif approx == "crc":
        raise NotImplementedError("CRC support not implemented yet.")

    else:
        raise ValueError(f"Unknown approximation: {approx!r}")

    if len(sys.argv) > 1 and sys.argv[1] == "print_params":
        print_optical_potentials(entrance_pot, exit_pot, config)
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
        entrance_pot,
        exit_pot,
        config,
    )


if __name__ == "__main__":
    main()