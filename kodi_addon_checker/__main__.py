import os
import argparse
from kodi_addon_checker.check_repo import check_repo


def dir_type(dir_path):
    """ArgParse callable to validate positional add-on arguments

    Arguments:
        dir_path {string} -- user defined argument

    Raises:
        argparse.ArgumentTypeError -- thrown when user input is not a directory or does not contain addon.xml

    Returns:
        string -- absolute path of the input directory
    """
    if not os.path.isdir(dir_path):
        raise argparse.ArgumentTypeError(
            "Add-on directory %s does not exist" % dir_path)
    elif not os.path.isfile(os.path.join(dir_path, "addon.xml")):
        raise argparse.ArgumentTypeError(
            "%s does not contain addon.xml" % dir_path)
    return os.path.abspath(dir_path)


def main():
    """The entry point to kodi-addon-checker
    """
    parser = argparse.ArgumentParser(prog="kodi-addon-checker",
                                     description="Checks Kodi repo for best practices and creates \
                                     problem and warning reports.\r\nIf optional add-on \
                                     directories are provided, check only those add-ons. \
                                     Otherwise, scan current repository and check all add-ons in \
                                     the current directory.")
    parser.add_argument("--version", action="version",
                        version="%(prog)s 0.0.1")
    parser.add_argument("add_on", metavar="add-on", type=dir_type, nargs="*",
                        help="optional add-on directories")
    args = parser.parse_args()
    check_repo(os.path.abspath(os.getcwd()), args.add_on)


if __name__ == "__main__":
    main()
