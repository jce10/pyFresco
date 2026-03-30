from __future__ import annotations

from fractions import Fraction


def parse_jpi(jpi_str: str) -> tuple[Fraction, int]:
    """
    Parse a spin-parity string like:
        '1/2+'
        '3/2-'
        '2+'
        '0-'

    Returns
    -------
    J : Fraction
        Spin as a Fraction.
    parity : int
        +1 or -1.
    """
    s = jpi_str.strip().replace(" ", "")
    if not s:
        raise ValueError("Empty Jπ field.")

    if s[-1] not in ["+", "-"]:
        raise ValueError(
            f"Could not parse parity from '{jpi_str}'. "
            "Use forms like 1/2+, 3/2-, 2+, 0-."
        )

    parity = +1 if s[-1] == "+" else -1
    j_str = s[:-1]

    if not j_str:
        raise ValueError(f"Could not parse spin from '{jpi_str}'.")

    try:
        J = Fraction(j_str)
    except Exception as exc:
        raise ValueError(
            f"Could not parse spin from '{jpi_str}'. "
            "Use integers or fractions like 2, 1/2, 3/2."
        ) from exc

    if J < 0:
        raise ValueError("Spin must be non-negative.")

    return J, parity


def parse_spin(spin_str: str) -> Fraction:
    """
    Parse the transferred particle spin.
    Examples:
        '0', '1/2', '1', '3/2'
    """
    s = spin_str.strip().replace(" ", "")
    if not s:
        raise ValueError("Transferred spin field is empty.")

    try:
        value = Fraction(s)
    except Exception as exc:
        raise ValueError(
            f"Could not parse transferred spin '{spin_str}'. "
            "Use values like 0, 1/2, 1, 3/2."
        ) from exc

    if value < 0:
        raise ValueError("Transferred spin must be non-negative.")

    return value


def parity_symbol(parity: int) -> str:
    """
    Convert parity integer to display symbol.
    """
    if parity not in (+1, -1):
        raise ValueError("Parity must be +1 or -1.")
    return "+" if parity == +1 else "-"


def orbital_parity(l_value: int) -> int:
    """
    Return (-1)^l as +1 or -1.
    """
    if l_value < 0:
        raise ValueError("Orbital angular momentum l must be non-negative.")
    return +1 if l_value % 2 == 0 else -1


def allowed_j_values(l_value: int, spin: Fraction) -> list[Fraction]:
    """
    Return allowed total angular momenta j from coupling orbital l and spin s:

        j = |l-s|, |l-s| + 1, ..., l+s
    """
    if l_value < 0:
        raise ValueError("Orbital angular momentum l must be non-negative.")
    if spin < 0:
        raise ValueError("Spin must be non-negative.")

    l_frac = Fraction(l_value, 1)
    j_min = abs(l_frac - spin)
    j_max = l_frac + spin

    values: list[Fraction] = []
    j = j_min
    while j <= j_max:
        values.append(j)
        j += 1

    return values


def can_couple(J_initial: Fraction, j_value: Fraction, J_final: Fraction) -> bool:
    """
    Check whether J_initial and j_value can couple to J_final:

        |J_initial - j| <= J_final <= J_initial + j
    """
    return abs(J_initial - j_value) <= J_final <= (J_initial + j_value)


def required_orbital_parity(
    pi_initial: int,
    pi_final: int,
    transferred_parity: int,
) -> int:
    """
    Determine the required parity of (-1)^l from:

        pi_final = pi_initial * pi_particle * (-1)^l

    Returns
    -------
    int
        +1 for even-l requirement, -1 for odd-l requirement.
    """
    if pi_initial not in (+1, -1):
        raise ValueError("Initial parity must be +1 or -1.")
    if pi_final not in (+1, -1):
        raise ValueError("Final parity must be +1 or -1.")
    if transferred_parity not in (+1, -1):
        raise ValueError("Transferred-particle parity must be +1 or -1.")

    return pi_final * pi_initial * transferred_parity


def parity_family(required_parity: int) -> str:
    """
    Convert required orbital parity to a human-readable family.
    """
    if required_parity == +1:
        return "even l only"
    if required_parity == -1:
        return "odd l only"
    raise ValueError("Required orbital parity must be +1 or -1.")


def find_allowed_l(
    jpi_initial: str,
    jpi_final: str,
    transferred_spin: str | Fraction,
    transferred_parity: int = +1,
    l_max: int = 8,
) -> dict:
    """
    Find allowed orbital angular momentum transfers l using:
      1. parity conservation
      2. angular momentum coupling rules

    Parameters
    ----------
    jpi_initial : str
        Initial state, e.g. '1/2+', '3/2-'
    jpi_final : str
        Final state, e.g. '2+', '1/2-'
    transferred_spin : str or Fraction
        Spin of the transferred particle/cluster
    transferred_parity : int
        Intrinsic parity of the transferred particle/cluster (+1 or -1)
    l_max : int
        Maximum l value to test

    Returns
    -------
    dict
        Dictionary containing parsed quantum numbers, parity info,
        allowed l values, allowed j values, and lowest allowed l.
    """
    J_initial, pi_initial = parse_jpi(jpi_initial)
    J_final, pi_final = parse_jpi(jpi_final)

    spin = (
        transferred_spin
        if isinstance(transferred_spin, Fraction)
        else parse_spin(str(transferred_spin))
    )

    if l_max < 0:
        raise ValueError("l_max must be non-negative.")

    req_parity = required_orbital_parity(
        pi_initial=pi_initial,
        pi_final=pi_final,
        transferred_parity=transferred_parity,
    )

    parity_text = (
        "Parity condition: πf = πi × πparticle × (-1)^l\n"
        f"                 {parity_symbol(pi_final)} = "
        f"{parity_symbol(pi_initial)} × {parity_symbol(transferred_parity)} × (-1)^l\n"
        f"Therefore, (-1)^l must be {parity_symbol(req_parity)}."
    )

    allowed_results: list[dict] = []

    for l_value in range(l_max + 1):
        if orbital_parity(l_value) != req_parity:
            continue

        j_candidates = allowed_j_values(l_value, spin)
        working_j = [
            j_value for j_value in j_candidates
            if can_couple(J_initial, j_value, J_final)
        ]

        if working_j:
            allowed_results.append(
                {
                    "l": l_value,
                    "all_j": j_candidates,
                    "allowed_j": working_j,
                }
            )

    lowest_allowed_l = allowed_results[0]["l"] if allowed_results else None

    return {
        "J_initial": J_initial,
        "pi_initial": pi_initial,
        "J_final": J_final,
        "pi_final": pi_final,
        "transferred_spin": spin,
        "transferred_parity": transferred_parity,
        "l_max": l_max,
        "required_orbital_parity": req_parity,
        "parity_family": parity_family(req_parity),
        "parity_requirement_text": parity_text,
        "allowed": allowed_results,
        "lowest_allowed_l": lowest_allowed_l,
    }