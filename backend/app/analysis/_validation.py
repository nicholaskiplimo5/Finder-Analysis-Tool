import numpy as np

N_DIGITS = 10


def validate_digit_array(digits: np.ndarray) -> np.ndarray:
    """Common validation for a raw last-digit series: 1-D, non-empty,
    whole numbers, each value in [0, 9]. Returns an int64 array."""
    digits = np.asarray(digits)
    if digits.ndim != 1:
        raise ValueError("digits must be a 1-D array")
    if digits.size == 0:
        raise ValueError("digits must be non-empty")
    if not np.issubdtype(digits.dtype, np.integer):
        if not np.all(np.equal(np.mod(digits, 1), 0)):
            raise ValueError("digits must be whole numbers")
        digits = digits.astype(np.int64)
    if digits.min() < 0 or digits.max() > 9:
        raise ValueError("digits must be in [0, 9]")
    return digits
