"""
    Copyright (C) 2017-2018 Team Kodi
    This file is part of Kodi - kodi.tv

    SPDX-License-Identifier: GPL-3.0-only
    See LICENSES/README.md for more information.
"""

import argparse
import logging
import os
import sys

from kodi_addon_checker import __version__, check_addon, ValidKodiVersions
from kodi_addon_checker.check_repo import check_repo
from kodi_addon_checker.common import load_plugins
from kodi_addon_checker.config import Config, ConfigManager
from kodi_addon_checker.logger import Logger
from kodi_addon_checker.record import INFORMATION, PROBLEM, WARNING, Record
from kodi_addon_checker.report import Report


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


def check_artifact(artifact_path, args, all_repo_addons):
    """
    Check given artifact and return its report. The artifact can be either an add-on or a repository.
    :param artifact_path: the path of add-on or repo
    :param args: argparse object
    :return: report
    """
    logger = logging.getLogger(__package__)
    logger.info("Downloading all repo addon list")
    logger.info("Download completed")
    artifact_path = os.path.abspath(artifact_path)
    config = Config(artifact_path, args)
    ConfigManager.process_config(config)
    if os.path.isfile(os.path.join(artifact_path, "addon.xml")):
        return check_addon.start(artifact_path, args, all_repo_addons, config)

    return check_repo(artifact_path, args, all_repo_addons, config)


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
                        version="%(prog)s {version}".format(version=__version__))
    parser.add_argument("dir", type=dir_type, nargs="*", help="optional add-on or repo directories")
    parser.add_argument("--branch", choices=ValidKodiVersions, required=True,
                        help="Target branch name where the checker will resolve dependencies")
    parser.add_argument("--PR", help="Tell if tool is to run on a pull requests or not", action='store_true')
    parser.add_argument("--allow-folder-id-mismatch", help="Allow the addon's folder name and id to mismatch",
                        action="store_true")
    parser.add_argument("--enable-debug-log", help="Enable debug logging to kodi-addon-checker.log",
                        action="store_true", default=False)
    ConfigManager.fill_cmd_args(parser)
    args = parser.parse_args()

    log_file_name = os.path.join(os.getcwd(), "kodi-addon-checker.log")
    Logger.create_logger(log_file_name, __package__, args.enable_debug_log)

    all_repo_addons = check_addon.get_all_repo_addons()

    if args.dir:
        # Following report is a wrapper for all sub reports
        report = Report("")
        for directory in args.dir:
            report.add(check_artifact(directory, args, all_repo_addons))
    else:
        report = check_artifact(os.getcwd(), args, all_repo_addons)

    if report.problem_count > 0:
        report.add(Record(PROBLEM, "We found %s problems and %s warnings, please check the logfile." %
                          (report.problem_count, report.warning_count)))
        sys.exit(1)
    elif report.warning_count > 0:
        report.add(Record(WARNING, "We found no problems and %s warnings, please check the logfile." %
                          report.warning_count))
    else:
        report.add(Record(INFORMATION, "We found no problems and no warnings, please enjoy your day."))


if __name__ == "__main__":
    main()
