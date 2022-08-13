import os


def create_directory(path: str) -> None:
    """
    Create a directory recursively.
    """
    path = os.path.realpath(path)
    if os.path.isdir(path) and os.path.exists(path):
        if len(os.listdir(path)) != 0:
            raise ValueError("%s is not an empty directory" % path)
    os.makedirs(path, exist_ok=True)
