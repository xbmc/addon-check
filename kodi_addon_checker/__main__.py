import argparse
import os
import logging
from kodi_addon_checker import logger
from kodi_addon_checker import check_addon
from kodi_addon_checker.check_repo import check_repo
from kodi_addon_checker.common import load_plugins
from kodi_addon_checker.config import ConfigManager, Config
from kodi_addon_checker.record import Record, PROBLEM, WARNING, INFORMATION
from kodi_addon_checker.report import Report
from kodi_addon_checker.reporter import ReportManager

ROOT_URL = "http://mirrors.kodi.tv/addons/{branch}/addons.xml"


def _all_repo_addons():
    branches = ['gotham', 'helix', 'isengard', 'jarvis', 'krypton', 'leia']
    repo_addons = {}

    for branch in branches:
        branch_url = ROOT_URL.format(branch=branch)
        repo_addons[branch] = check_addon._get_addons(branch_url)

    return repo_addons


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


def check_artifact(artifact_path, args, branch_name):
    """
    Check given artifact and return its report. The artifact can be either an add-on or a repository.
    :param artifact_path: the path of add-on or repo
    :param args: argparse object
    :return: report
    """
    all_repo_addons = _all_repo_addons()
    artifact_path = os.path.abspath(artifact_path)
    config = Config(artifact_path, args)
    ConfigManager.process_config(config)
    if os.path.isfile(os.path.join(artifact_path, "addon.xml")):
        return check_addon.start(artifact_path, branch_name, all_repo_addons, config)
    else:
        return check_repo(artifact_path, branch_name, all_repo_addons, config)


def main():
    """The entry point to kodi-addon-checker
    """
    choice = ['gotham', 'helix', 'isengard', 'jarvis', 'krypton', 'leia']
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
    parser.add_argument("--branch", choices=choice, required=True,
                        help="Target branch name where the checker will resolve dependencies")
    ConfigManager.fill_cmd_args(parser)
    args = parser.parse_args()

    log_file_name = os.path.join(os.getcwd(), "kodi-addon-checker.log")
    logger.Logger.create_logger(log_file_name, __package__)

    if args.dir:
        # Following report is a wrapper for all sub reports
        report = Report("")
        for directory in args.dir:
            report.add(check_artifact(directory, args, args.branch))
    else:
        report = check_artifact(os.getcwd(), args, args.branch)

    if report.problem_count > 0:
        report.add(Record(PROBLEM, "We found %s problems and %s warnings, please check the logfile." %
                          (report.problem_count, report.warning_count)))
    elif report.warning_count > 0:
        report.add(Record(WARNING, "We found no problems and %s warnings, please check the logfile." %
                          report.warning_count))
    else:
        report.add(Record(INFORMATION, "We found no problems and no warnings, please enjoy your day."))

    ReportManager.report(report)


if __name__ == "__main__":
    main()
