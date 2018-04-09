import argparse
import os

from kodi_addon_checker import check_addon
from kodi_addon_checker.check_repo import check_repo
from kodi_addon_checker.common import load_plugins
from kodi_addon_checker.config import ConfigManager, Config
from kodi_addon_checker.record import Record, INFORMATION, PROBLEM, WARNING
from kodi_addon_checker.report import Report
from kodi_addon_checker.reporter import ReportManager


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
    return os.path.abspath(dir_path)


def main():
    """The entry point to kodi-addon-checker
    """
    load_plugins()
    parser = argparse.ArgumentParser(prog="kodi-addon-checker",
                                     description="Checks Kodi repo for best practices and creates \
                                     problem and warning reports.\r\nIf optional add-on \
                                     directories are provided, check only those add-ons. \
                                     Otherwise, scan current repository and check all add-ons in \
                                     the current directory.")
    parser.add_argument("--version", action="version",
                        version="%(prog)s 0.0.1")
    parser.add_argument("dir", type=dir_type, nargs="*", help="optional add-on or repo directories")
    ConfigManager.fill_cmd_args(parser)
    args = parser.parse_args()

    current_dir = os.path.abspath(os.getcwd())
    if args.dir:
        report = Report(current_dir)
        for directory in args.dir:
            if os.path.isfile(os.path.join(directory, "addon.xml")):
                report.add(Record(INFORMATION, "Checking add-on %s" % directory))
                # For add-ons try to load .tests-config.json from current directory
                config = Config(current_dir, args)
                addon_report = check_addon.start(os.path.abspath(directory), config)
                report.add(addon_report)
            else:
                repo_path = os.path.abspath(directory)
                # Load .tests-config.json from repo directory
                config = Config(repo_path, args)
                repo_report = check_repo(repo_path, config)
                report.add(repo_report)
    else:
        # Treat current directory as repo
        config = Config(current_dir, args)
        report = check_repo(current_dir, config)

    if report.problem_count > 0:
        report.add(Record(PROBLEM, "We found %s problems and %s warnings, please check the logfile." %
                          (report.problem_count, report.warning_count)))
    elif report.warning_count > 0:
        report.add(Record(WARNING, "We found %s problems and %s warnings, please check the logfile." %
                          (report.problem_count, report.warning_count)))

    ReportManager.report(report)


if __name__ == "__main__":
    main()
