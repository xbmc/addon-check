import os
import sys

import kodi_addon_checker.check_addon as check_addon
from kodi_addon_checker.common import colorPrint
from kodi_addon_checker.report import Report, INFORMATION, Record, ReportManager


def check_repo(config, repo_path, parameters):
    repo_report = Report()
    repo_report.log(Record(INFORMATION, "Checking repository %s" % repo_path))
    print("Repo path " + repo_path)
    if len(parameters) == 0:
        toplevel_folders = sorted(next(os.walk(repo_path))[1])
    else:
        toplevel_folders = sorted(parameters)

    print("Toplevel folders " + str(toplevel_folders))

    for addon_folder in toplevel_folders:
        if addon_folder[0] != '.':
            repo_report.log(Record(INFORMATION, "Checking add-on %s" % addon_folder))
            addon_path = os.path.join(repo_path, addon_folder)
            addon_report = check_addon.start(addon_path, config)
            repo_report.log(addon_report)

    ReportManager.report(repo_report)

    if repo_report.problem_count > 0:
        colorPrint("We found %s problems and %s warnings, please check the logfile." % (
            repo_report.problem_count, repo_report.warning_count), "31")
        sys.exit(1)
    elif repo_report.warning_count > 0:
        # If we only found warning, don't mark the build as broken
        colorPrint("We found %s problems and %s warnings, please check the logfile." % (
            repo_report.problem_count, repo_report.warning_count), "35")

    print("Finished!")
