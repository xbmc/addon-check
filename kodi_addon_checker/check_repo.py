import os

import kodi_addon_checker.check_addon as check_addon
from kodi_addon_checker.record import INFORMATION, Record, PROBLEM, WARNING
from kodi_addon_checker.report import Report
from kodi_addon_checker.reporter import ReportManager


def check_repo(config, repo_path, parameters):
    repo_report = Report(repo_path)
    repo_report.add(Record(INFORMATION, "Checking repository %s" % repo_path))
    if len(parameters) == 0:
        toplevel_folders = sorted(next(os.walk(repo_path))[1])
    else:
        toplevel_folders = sorted(parameters)

    for addon_folder in toplevel_folders:
        if addon_folder[0] != '.':
            repo_report.add(Record(INFORMATION, "Checking add-on %s" % addon_folder))
            addon_path = os.path.join(repo_path, addon_folder)
            addon_report = check_addon.start(addon_path, config)
            repo_report.add(addon_report)

    if repo_report.problem_count > 0:
        repo_report.add(Record(PROBLEM, "We found %s problems and %s warnings, please check the logfile." %
                               (repo_report.problem_count, repo_report.warning_count)))
    elif repo_report.warning_count > 0:
        repo_report.add(Record(WARNING, "We found %s problems and %s warnings, please check the logfile." %
                               (repo_report.problem_count, repo_report.warning_count)))
    else:
        repo_report.add(Record(INFORMATION, "We found no problems and no warnings, please enjoy your day."))

    ReportManager.report(repo_report)
