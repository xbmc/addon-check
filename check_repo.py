import os
import sys
import check_addon
from common import colorPrint


def check_repo():
    error_counter = {"warnings": 0, "problems": 0}
    repo_path = os.path.abspath(os.path.join(
        os.path.dirname(os.path.realpath(__file__)), os.pardir))
    print("Repo path " + repo_path)

    toplevel_folders = next(os.walk(repo_path))[1]
    print("Toplevel folders " + str(toplevel_folders))

    for addon_folder in toplevel_folders:
        if addon_folder[0] != '.':
            addon_path = os.path.join(repo_path, addon_folder)
            error_counter = check_addon.check_addon(error_counter, addon_path)

    if error_counter["problems"] > 0:
        colorPrint("We found %s problems and %s warnings, please check the logfile." % (
            error_counter["problems"], error_counter["warnings"]), "31")
        sys.exit(1)
    elif error_counter["warnings"] > 0:
        # If we only found warnings, don't mark the build as broken
        colorPrint("We found %s problems and %s warnings, please check the logfile." % (
            error_counter["problems"], error_counter["warnings"]), "35")

    print("Finished!")

check_repo()
