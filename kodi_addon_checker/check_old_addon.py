"""
    Copyright (C) 2017-2018 Team Kodi
    This file is part of Kodi - kodi.tv

    SPDX-License-Identifier: GPL-3.0-only
    See LICENSES/README.md for more information.
"""

import logging
import os
import xml.etree.ElementTree as ET
from distutils.version import LooseVersion

from .record import INFORMATION, PROBLEM, Record
from .report import Report

LOGGER = logging.getLogger(__name__)


def check_for_existing_addon(report: Report, addon_path: str, all_repo_addons: dict, pr: bool):
    """Check if addon submitted already exists or not
        :addon_path: path of the addon
        :all_repo_addons: dictionary return by all_repo_addon() function
    """

    addon_xml = os.path.join(addon_path, "addon.xml")
    addon_name, addon_version = _get_addon_name(addon_xml)

    for branch, repo in sorted(all_repo_addons.items()):
        if addon_name in repo:
            _check_versions(report, addon_name, branch, addon_version, repo.find(addon_name).version, pr)
            return

    report.add(Record(INFORMATION, "This is a new addon"))


def _get_addon_name(xml_path: str):
    """returns name and version of the addon
        :xml_path: path of the xml file
    """

    tree = ET.parse(xml_path).getroot()
    return (tree.get("id"), tree.get("version"))


def _check_versions(report: Report, addon_name, branch, addon_version, repo_addons_version, pr):
    """Check for version bump in the existing addon

        :addon_name:         addon that is to be checked
        :addon_version:      the version of addon that is submitted
        :repo_addon_version: version of addon present in Kodi repository
        :pr:                 boolean value indicating whether the check is
                             running on pull request or not
    """
    if pr:
        if LooseVersion(addon_version) > LooseVersion(repo_addons_version):
            LOGGER.info("%s addon have greater version: %s than repo_version: %s in branch %s",
                        addon_name, addon_version, repo_addons_version, branch)
        else:
            report.add(Record(PROBLEM, "%s addon already exists with version: %s in %s branch"
                              % (addon_name, repo_addons_version, branch)))
    else:
        if LooseVersion(addon_version) < LooseVersion(repo_addons_version):
            report.add(Record(PROBLEM, "%s addon already exist with version: %s in %s branch"
                              % (addon_name, repo_addons_version, branch)))
        else:
            report.add(Record(INFORMATION, "%s addon also exists in %s branch but with version: %s"
                              % (addon_name, branch, repo_addons_version)))
