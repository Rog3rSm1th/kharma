import random


def random_int(min: int, max: int) -> int:
    """
    Generate a random integer between min and max values.
    """
    if min == max:
        return min
    else:
        return random.randrange(min, max + 1)
