from __future__ import annotations

from typing import Final


# ------------------------------------------------------------------
# Common transferred-particle presets
# ------------------------------------------------------------------

PARTICLE_PRESETS: Final[dict[str, dict[str, str]]] = {
    "neutron": {
        "spin": "1/2",
        "parity": "+",
        "label": "n",
    },
    "proton": {
        "spin": "1/2",
        "parity": "+",
        "label": "p",
    },
    "alpha": {
        "spin": "0",
        "parity": "+",
        "label": "α",
    },
    "deuteron": {
        "spin": "1",
        "parity": "+",
        "label": "d",
    },
    "triton": {
        "spin": "1/2",
        "parity": "+",
        "label": "t",
    },
    "3He": {
        "spin": "1/2",
        "parity": "+",
        "label": r"$^3$He",
    },
}


# ------------------------------------------------------------------
# Spectroscopic letter mapping for orbital angular momentum l
# ------------------------------------------------------------------

SPECTRO_SYMBOLS: Final[dict[int, str]] = {
    0: "s",
    1: "p",
    2: "d",
    3: "f",
    4: "g",
    5: "h",
    6: "i",
    7: "j",
    8: "k",
    9: "l",
    10: "m",
}


# ------------------------------------------------------------------
# Example configurations for quick-loading in the GUI
# ------------------------------------------------------------------

EXAMPLE_CASES: Final[dict[str, dict[str, str]]] = {
    "29Si(d,p)30Si*(2+)": {
        "initial_jpi": "1/2+",
        "final_jpi": "2+",
        "particle": "neutron",
        "spin": "1/2",
        "parity": "+",
        "l_max": "8",
        "notes": "Neutron transfer example to the first excited 2+ state in 30Si.",
    },
    "9Be(6Li,d)13C*(1/2-) alpha transfer": {
        "initial_jpi": "3/2-",
        "final_jpi": "1/2-",
        "particle": "alpha",
        "spin": "0",
        "parity": "+",
        "l_max": "8",
        "notes": "Alpha-transfer example for the 13C excited state assignment check.",
    },
    "Blank": {
        "initial_jpi": "",
        "final_jpi": "",
        "particle": "neutron",
        "spin": "1/2",
        "parity": "+",
        "l_max": "8",
        "notes": "Empty form for manual entry.",
    },
}


# ------------------------------------------------------------------
# Default values used when initializing the GUI
# ------------------------------------------------------------------

DEFAULT_GUI_VALUES: Final[dict[str, str]] = {
    "initial_jpi": "1/2+",
    "final_jpi": "2+",
    "particle": "neutron",
    "spin": "1/2",
    "parity": "+",
    "l_max": "8",
    "example": "29Si(d,p)30Si*(2+)",
}


# ------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------

def get_particle_names(include_custom: bool = True) -> list[str]:
    """
    Return the list of available particle preset names.

    Parameters
    ----------
    include_custom : bool
        If True, append 'custom' to the returned list.

    Returns
    -------
    list[str]
        Ordered particle preset names for GUI dropdown use.
    """
    names = list(PARTICLE_PRESETS.keys())
    if include_custom:
        names.append("custom")
    return names


def get_particle_preset(name: str) -> dict[str, str] | None:
    """
    Return a particle preset dictionary if it exists.

    Parameters
    ----------
    name : str
        Preset name, e.g. 'neutron', 'alpha'

    Returns
    -------
    dict[str, str] | None
        Preset dictionary or None if not found.
    """
    return PARTICLE_PRESETS.get(name)


def get_example_names() -> list[str]:
    """
    Return the list of available quick-load example names.
    """
    return list(EXAMPLE_CASES.keys())


def get_example_case(name: str) -> dict[str, str] | None:
    """
    Return an example case dictionary if it exists.
    """
    return EXAMPLE_CASES.get(name)


def spectro_symbol(l_value: int) -> str:
    """
    Return the spectroscopic letter corresponding to orbital angular momentum l.

    Examples
    --------
    l = 0 -> 's'
    l = 1 -> 'p'
    l = 2 -> 'd'
    """
    return SPECTRO_SYMBOLS.get(l_value, f"l={l_value}")


def shell_label(l_value: int) -> str:
    """
    Return a lightweight shell-style label for display purposes.

    Notes
    -----
    This uses the minimal oscillator-shell style choice N = l,
    corresponding to the lowest radial choice n = 0.
    It is a display helper, not a nucleus-specific shell-model assignment.
    """
    return f"N = {l_value}, {spectro_symbol(l_value)}-wave"