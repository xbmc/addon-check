import os
import sys
import json
import kodi_addon_checker.check_addon as check_addon
from kodi_addon_checker.common import colorPrint


def _read_config_for_version(repo_path):
    config_path = os.path.join(repo_path, '.tests-config.json')
    if os.path.isfile(config_path):
        with open(config_path) as json_data:
            return json.load(json_data)

    return None


def check_repo(repo_path, parameters):
    error_counter = {"warnings": 0, "problems": 0}
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
            error_counter = check_addon.start(
                error_counter, addon_path, config)

    if error_counter["problems"] > 0:
        colorPrint("We found %s problems and %s warnings, please check the logfile." % (
            error_counter["problems"], error_counter["warnings"]), "31")
        sys.exit(1)
    elif error_counter["warnings"] > 0:
        # If we only found warnings, don't mark the build as broken
        colorPrint("We found %s problems and %s warnings, please check the logfile." % (
            error_counter["problems"], error_counter["warnings"]), "35")

    print("Finished!")
