from kharma.app.utils.config import Config


def parse_integer(integer: str) -> int:
    """
    Parse an integer string between -infinity and +infinity and return
    an integer between -1 * Config.MAX_INT_VALUE and Config.MAX_INT_VALUE
    """
    if integer == "infinity":
        return Config.MAX_INT_VALUE
    if integer == "-infinity":
        return -1 * Config.MAX_INT_VALUE
    else:
        return max(min(int(integer), Config.MAX_INT_VALUE), -1 * Config.MAX_INT_VALUE)
