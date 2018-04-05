import json
import os
import sys

import kodi_addon_checker.check_addon as check_addon
from kodi_addon_checker.common import colorPrint
from kodi_addon_checker.plugins.console_reporter import ConsoleReporter
from kodi_addon_checker.report import Report


def _read_config_for_version(repo_path):
    config_path = os.path.join(repo_path, '.tests-config.json')
    if os.path.isfile(config_path):
        with open(config_path) as json_data:
            return json.load(json_data)

    return None


def check_repo(repo_path, parameters):
    repo_report = Report(repo_path)
    print("Repo path " + repo_path)
    if len(parameters) == 0:
        toplevel_folders = sorted(next(os.walk(repo_path))[1])
    else:
        toplevel_folders = sorted(parameters)

    print("Toplevel folders " + str(toplevel_folders))

    config = _read_config_for_version(repo_path)

    for addon_folder in toplevel_folders:
        if addon_folder[0] != '.':
            addon_path = os.path.join(repo_path, addon_folder)
            addon_report = check_addon.start(addon_path, config)
            repo_report.log(addon_report)

    # Report using ConsoleReporter
    reporter = ConsoleReporter()
    reporter.report(repo_report)

    if repo_report.problem > 0:
        colorPrint("We found %s problem and %s warning, please check the logfile." % (
            repo_report.problem, repo_report.warning), "31")
        sys.exit(1)
    elif repo_report.warning > 0:
        # If we only found warning, don't mark the build as broken
        colorPrint("We found %s problem and %s warning, please check the logfile." % (
            repo_report.problem, repo_report.warning), "35")

    print("Finished!")
