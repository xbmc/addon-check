"""
    Copyright (C) 2017-2018 Team Kodi
    This file is part of Kodi - kodi.tv

    SPDX-License-Identifier: GPL-3.0-only
    See LICENSES/README.md for more information.
"""

import os

from kodi_addon_checker import check_addon

from .record import INFORMATION, PROBLEM, Record
from .report import Report


def check_repo(repo_path, args, all_repo_addons, config):
    """Perform all the check on a complete repository

        :repo_path: Path of the repo that is to be tested
        :args: argparse object
        :all_repo_addons: a nested list having information
                          about all the repo addons
        :config: Config object
    """
    repo_report = Report(repo_path)
    repo_report.add(Record(INFORMATION, f"Checking repository {repo_path}"))
    toplevel_folders = sorted(next(os.walk(repo_path))[1])

    for addon_folder in toplevel_folders:
        if addon_folder[0] != '.':
            addon_path = os.path.join(repo_path, addon_folder)
            try:
                addon_report = check_addon.start(addon_path, args, all_repo_addons, config)
                repo_report.add(addon_report)
            except Exception as e: # pylint: disable=broad-except
                repo_report.add(Record(PROBLEM, f"Something went wrong. Please see: {e}"))
    return repo_report
