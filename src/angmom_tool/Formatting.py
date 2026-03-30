from __future__ import annotations

from fractions import Fraction

from angmom_tool.Presets import shell_label
from angmom_tool.SelectionRules import parity_symbol


def format_fraction(frac: Fraction) -> str:
    """
    Format a Fraction for clean display.

    Examples
    --------
    Fraction(2, 1)   -> '2'
    Fraction(3, 2)   -> '3/2'
    """
    if frac.denominator == 1:
        return str(frac.numerator)
    return f"{frac.numerator}/{frac.denominator}"


def format_jpi(J: Fraction, parity: int) -> str:
    """
    Format spin and parity together as a Jπ string.

    Examples
    --------
    Fraction(1, 2), +1 -> '1/2+'
    Fraction(2, 1), -1 -> '2-'
    """
    return f"{format_fraction(J)}{parity_symbol(parity)}"


def build_parity_summary(result: dict) -> str:
    """
    Return the parity-condition summary block from a result dictionary.
    """
    return result["parity_requirement_text"]


def build_coupling_summary() -> str:
    """
    Return a standard summary of the angular-momentum coupling logic.
    """
    lines = [
        "Coupling rule used:",
        "  1) j = l ⊕ s  ->  j = |l-s| ... l+s",
        "  2) Jf must satisfy |Ji-j| ≤ Jf ≤ Ji+j",
    ]
    return "\n".join(lines)


def build_allowed_l_block(result: dict) -> str:
    """
    Build the section listing all allowed l values and their allowed j values.
    """
    lines: list[str] = []

    if not result["allowed"]:
        lines.append("No allowed l values were found up to the chosen l_max.")
        return "\n".join(lines)

    lines.append("Allowed l values:")

    for item in result["allowed"]:
        l_value = item["l"]
        all_j_str = ", ".join(format_fraction(j) for j in item["all_j"])
        allowed_j_str = ", ".join(format_fraction(j) for j in item["allowed_j"])
        marker = "   <-- lowest allowed l" if l_value == result["lowest_allowed_l"] else ""

        lines.append(f"  l = {l_value}   ({shell_label(l_value)})")
        lines.append(f"      all j from l⊕s:     {all_j_str}")
        lines.append(f"      j values giving Jf: {allowed_j_str}{marker}")

    return "\n".join(lines)


def build_lowest_l_summary(result: dict) -> str:
    """
    Build a compact one-line summary of the lowest allowed transfer.
    """
    lowest_l = result.get("lowest_allowed_l")
    if lowest_l is None:
        return "No allowed l values found up to the chosen l_max."

    return (
        f"Lowest allowed transfer: l = {lowest_l} "
        f"({shell_label(lowest_l)}); "
        f"parity filter gives {result['parity_family']}."
    )


def build_report(result: dict, particle_name: str = "custom") -> str:
    """
    Build the full plain-text report shown in the GUI.
    """
    lines: list[str] = []

    lines.append("Allowed Angular Momentum Transfer Report")
    lines.append("=" * 44)
    lines.append("")

    lines.append(
        f"Initial state:      Jπ = {format_jpi(result['J_initial'], result['pi_initial'])}"
    )
    lines.append(
        f"Final state:        Jπ = {format_jpi(result['J_final'], result['pi_final'])}"
    )
    lines.append(f"Transferred particle: {particle_name}")
    lines.append(
        f"Transferred spin:   s  = {format_fraction(result['transferred_spin'])}"
    )
    lines.append(
        f"Transferred parity: π  = {parity_symbol(result['transferred_parity'])}"
    )
    lines.append(f"Maximum l checked:  {result['l_max']}")
    lines.append("")

    lines.append(build_parity_summary(result))
    lines.append(f"Parity filter result: {result['parity_family']}")
    lines.append("")
    lines.append(build_coupling_summary())
    lines.append("")
    lines.append(build_allowed_l_block(result))
    lines.append("")

    if result.get("lowest_allowed_l") is not None:
        lines.append(
            f"Lowest allowed l: {result['lowest_allowed_l']}   "
            f"({shell_label(result['lowest_allowed_l'])})"
        )

    lines.append("Physics note: this tool returns quantum-mechanically allowed l values only.")
    lines.append("The shell label shown here uses the lowest radial choice n = 0, so N = l.")
    lines.append("A fully nucleus-specific orbital assignment still needs shell-structure input.")

    return "\n".join(lines)