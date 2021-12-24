BLACK = -1
WHITE = 1


def as_str(color: int) -> str:
    """
    Converts the given color into a string.
    :param color: The color to represent as a string
    :return: String representation of color
    """
    if color not in [-1, 1]:
        return 'Undefined'
    return 'BLACK' if color == BLACK else 'WHITE'
