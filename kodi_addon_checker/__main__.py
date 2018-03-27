import os
import argparse
from kodi_addon_checker.check_repo import check_repo


def dir_type(dir_path):
    """ArgParse callable to validate positional directory arguments

    Arguments:
        dir_path {string} -- user defined argument

    Raises:
        argparse.ArgumentTypeError -- thrown when user input is not a directory

    Returns:
        string -- absolute path of the input directory
    """
    if not os.path.isdir(dir_path):
        raise argparse.ArgumentTypeError("%s is not a directory" % dir_path)
    return os.path.abspath(dir_path)


def main():
    """The entry point to kodi-addon-checker
    """
    parser = argparse.ArgumentParser(prog="kodi-addon-checker",
                                     description="Checks Kodi repo for best practices and creates problem and warning reports")
    parser.add_argument("--version", action="version",
                        version="%(prog)s 0.0.1")
    parser.add_argument("folders", type=dir_type, nargs="*")
    args = parser.parse_args()
    check_repo(os.path.abspath(os.getcwd()), args.folders)


if __name__ == "__main__":
    main()
