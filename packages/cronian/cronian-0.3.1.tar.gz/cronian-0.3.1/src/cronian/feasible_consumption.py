import re

import numpy as np


def calculate_flex_store_bounds(fd_name, fd_profile: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Calculate the min/max bounds of flexible demand modelled as a store.

    Flexible demand is modeled as a store with deadlines on its energy
    consumption levels. The max consumption level is determined by assuming that
    the flex demand is shifted to an earlier time (ahead) as much as allowed by
    the number of snapshots it can be shifted `n` (from `flex+n`).

    Args:
    -----
        fd_name: Name of the flexible demand profile (e.g., 'flex+2')
        fd_profile: The values of the flexible demand profile.

    Returns:
    --------
        e_min: The minimum feasible consumption level of the flexible demand.
        e_max: The maximum feasible consumption level of the flexible demand.
    """
    shift_hours = parse_flex_amount(fd_name)

    e_min = fd_profile.cumsum()
    e_max = np.empty_like(e_min)
    e_max[:-shift_hours] = e_min[shift_hours:]  # maximum is the minimum, but shifted forward
    e_max[-shift_hours:] = e_min[-1]  # fill the rest of the array with the final value
    return e_min, e_max


def parse_flex_amount(name: str) -> int | None:
    """Parse a demand name to extract the amount of flexibility if available.

    Args:
    -----
        name: Name of the flexible demand profile (e.g., 'flex+2')

    Returns:
    --------
        The amount of flexibility in hours if the name matches the pattern
            'flex+{n:d}', otherwise None.

    Raises:
    -------
        ValueError: if the flexible demand name does not match the pattern
            'flex+{n:d}'.
    """
    # Check that `flex+N` is (somewhere) in `name`, for some integer value of `N`
    match = re.search(r".*flex\+(\d+).*", name.lower())

    if match is None:
        raise ValueError(f"String '{name}' did not match the pattern 'flex+{{:d}}'")

    return int(match.group(1))
