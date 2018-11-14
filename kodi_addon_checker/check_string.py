"""
    Copyright (C) 2017-2018 Team Kodi
    This file is part of Kodi - kodi.tv

    SPDX-License-Identifier: GPL-3.0-only
    See LICENSES/README.md for more information.
"""

import os

from .report import Report
from .common import relative_path
from . import handle_files
from .record import PROBLEM, Record, WARNING


def check_for_legacy_strings_xml(report: Report, addon_path: str):
    """Find for the string.xml file in addon which was used in old versions
        :addon_path: path of the addon
    """
    for file in handle_files.find_files_recursive("strings.xml", os.path.join(addon_path, "resources", "language")):
        report.add(
            Record(PROBLEM, "Found %s please migrate to strings.po." % relative_path(file)))


def find_blacklisted_strings(report: Report, addon_path: str, problems: list, warnings: list, file_types: list):
    """Find for any blacklisted strings in the addons files
        :addon_path: Path of theh addon
        :problems: List of all the strings that will cause problem being in an addon
        :warnings: List of all the strings that shouldn't be in addon
                        but doesn't cause any problem
        :file_type: List of the whitelisted files to look into
    """
    for result in handle_files.find_in_file(addon_path, problems, file_types):
        report.add(Record(PROBLEM, "Found blacklisted term %s in file %s:%s (%s)"
                          % (result["term"], result["searchfile"], result["linenumber"], result["line"])))

    for result in handle_files.find_in_file(addon_path, warnings, file_types):
        report.add(Record(WARNING, "Found blacklisted term %s in file %s:%s (%s)"
                          % (result["term"], result["searchfile"], result["linenumber"], result["line"])))
