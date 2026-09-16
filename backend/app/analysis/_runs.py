import numpy as np


def run_lengths(x: np.ndarray) -> np.ndarray:
    """Lengths of maximal runs of equal consecutive values in `x`.

    E.g. [3, 3, 3, 7, 7, 2, 2, 2, 2] -> [3, 2, 4]. Shared by the
    streak-length test (runs of a repeated digit) and the rise/fall run
    test (runs of a repeated movement direction).
    """
    x = np.asarray(x)
    if x.size == 0:
        return np.array([], dtype=np.int64)
    change_points = np.flatnonzero(np.diff(x) != 0) + 1
    boundaries = np.concatenate(([0], change_points, [x.size]))
    return np.diff(boundaries).astype(np.int64)
