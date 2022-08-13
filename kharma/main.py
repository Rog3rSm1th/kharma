import os
from kharma.app import Kharma
from kharma.app.utils.arguments import parse_arguments
from kharma.app.utils.output import create_directory


def main() -> None:
    """
    Kharma entrypoint
    usage: kharma [-h] [-v] -t TEMPLATE -c COUNT [-s] {output} ...
    """
    args = parse_arguments()
    file_output = args.command == "output"

    # Initialize Kharma engine with the template
    try:
        kharma = Kharma(args.template, safe_mode=args.safe_mode)
    except Exception as e:
        print("Error: %s" % e)
        exit(1)

    # Create output directory
    if file_output:
        try:
            create_directory(args.directory)
        except Exception as e:
            print("Error: %s" % e)
            exit(1)

    for i in range(args.count):
        # Generate document from template
        try:
            document = kharma.generate()
        except Exception as e:
            print("Error: %s" % e)
            exit(1)

        # Save document to output file
        if file_output:
            if args.extension is None:
                file_name = "%s" % (str(i))
            else:
                file_name = "%s.%s" % (str(i), args.extension)
            file_path = os.path.realpath(os.path.join(args.directory, file_name))
            with open(file_path, "w+") as f:
                f.write(document)
        # Output document to stdout
        else:
            print(document)
    exit(0)
