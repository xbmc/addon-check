import os
import kodi_addon_checker.check_addon as check_addon
from .record import INFORMATION, PROBLEM, Record
from .report import Report


def check_repo(repo_path, branch_name, all_repo_addons, pr, config):
    repo_report = Report(repo_path)
    repo_report.add(Record(INFORMATION, "Checking repository %s" % repo_path))
    toplevel_folders = sorted(next(os.walk(repo_path))[1])

    for addon_folder in toplevel_folders:
        if addon_folder[0] != '.':
            addon_path = os.path.join(repo_path, addon_folder)
            try:
                addon_report = check_addon.start(addon_path, branch_name, all_repo_addons, pr, config)
                repo_report.add(addon_report)
            except Exception as e:
                repo_report.add(Record(PROBLEM, "Something went wrong. Please see: %s" % e))
    return repo_report
