import pathlib
from typing import Tuple, List


def build_path(filename, directory='source') -> pathlib.Path:
    root = pathlib.Path.cwd() / directory / filename
    return root


def readfile(filename: str, directory: str = 'source') -> Tuple[str, List[str]]:
    """Reads a file and outputs the text and an array of newline characters
    used at the end of each line.

    Parameters
    ----------
    filename : str
    directory : str, optional
        Directory of the file. The default is current directory.

    Returns
    -------
    text :
        File as a str
    n : TYPE
        List of strings that contain the types of new_line characters used in the file.
    """
    fn = build_path(filename, directory)
    n = []
    with fn.open("r") as f:
        lines = f.readlines()
        text = ''.join(lines)  # list(f))
        n.extend(f.newlines)
    return text, n
