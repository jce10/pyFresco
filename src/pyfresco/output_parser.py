"""
Module to extract angular distribution block from a FRESCO text output (e.g. fort.16 renamed)
and write a two-column .sorted file (angle, xsec) to out_dir.

Returns the path to the written .sorted file.

"""

import csv
from pathlib import Path
from rich.console import Console

console = Console()

def write_sorted_from_fresco_output(infile: str, out_dir: str, out_basename: str) -> str:
    angles = []
    cross_sections = []

    start_line = "@s1"
    end_line = "END"
    end_count = 0
    lines_after_start = 0
    between_lines = False

    with open(infile, "r") as f:
        for raw in f:
            line = raw.strip()

            if start_line in line:
                between_lines = True
                lines_after_start = 2
                continue

            if line == end_line:
                if end_count == 0:
                    end_count += 1
                    continue
                else:
                    between_lines = False
                    break

            if not between_lines:
                continue

            if lines_after_start > 0:
                lines_after_start -= 1
                continue

            parts = line.split()
            if len(parts) < 2:
                continue

            ang, xsec = parts[0], parts[1]
            angles.append(ang)
            cross_sections.append(xsec)

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    storefile = out_dir / f"{out_basename}.sorted"
    with open(storefile, "w", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerows(zip(angles, cross_sections))

    # console.print(f"[green]Successfully written file {storefile.name}!\n[/]")
    return str(storefile)