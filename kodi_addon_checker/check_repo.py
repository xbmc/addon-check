import os
import kodi_addon_checker.check_addon as check_addon
from kodi_addon_checker.record import INFORMATION, Record
from kodi_addon_checker.report import Report


def check_repo(repo_path, config, repo_addons):
    repo_report = Report(repo_path)
    repo_report.add(Record(INFORMATION, "Checking repository %s" % repo_path))
    toplevel_folders = sorted(next(os.walk(repo_path))[1])

    for addon_folder in toplevel_folders:
        if addon_folder[0] != '.':
            addon_path = os.path.join(repo_path, addon_folder)
            addon_report = check_addon.start(addon_path, repo_addons, config)
            repo_report.add(addon_report)

    return repo_report
