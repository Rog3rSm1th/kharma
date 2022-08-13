import argparse
import re
from kharma import __version__


def positive_integer(value: int) -> int:
    """
    Check if an integer is positive
    """
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return ivalue


def extension(value: str) -> str:
    """
    Check if an extension is valid
    """
    extension = value.lower()
    extension_regexp = re.compile("^[a-z0-9]+$")
    if not extension_regexp.match(extension):
        raise argparse.ArgumentTypeError("%s is an invalid extension" % extension)
    return extension


def parse_arguments() -> argparse.Namespace:
    """
    parse the command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="""
        Kharma is a state-of-the-art grammar fuzzer. It can generate many random documents 
        based on a grammar, which can be used to improve your testing corpus by increasing 
        code coverage and to find bugs/vulnerabilities in many kinds of applications 
        (interpreters, files parsers, etc...).
        """
    )
    # Version
    parser.add_argument("-v", "--version", action="version", version=__version__)

    # Template path
    parser.add_argument("-t", "--template", required=True, help="template path, e.g. ./path/to/file.kg")
    # Documents count
    parser.add_argument(
        "-c",
        "--count",
        required=True,
        type=positive_integer,  # type: ignore
        help="number of documents to generate",
    )

    # Safe-mode, disallow call statements
    parser.add_argument(
        "-s",
        "--safe-mode",
        required=False,
        action="store_true",
        help="disallow call statements",
    )

    # Output
    subparsers = parser.add_subparsers(help="sub-command help", dest="command")
    output_parser = subparsers.add_parser("output", help="output help")
    # Documents output directory
    output_parser.add_argument(
        "-d", "--directory", required=True, help="files output directory, e.g. ./path/to/directory"
    )
    # Extension of the documents
    output_parser.add_argument(
        "-e", "--extension", required=False, type=extension, help="files output extension, e.g. js"
    )

    args = parser.parse_args()
    return args
