"""
    Copyright (C) 2017-2018 Team Kodi
    This file is part of Kodi - kodi.tv

    SPDX-License-Identifier: GPL-3.0-only
    See LICENSES/README.md for more information.
"""

import logging
import os
import xml.etree.ElementTree as ET

from .record import INFORMATION, PROBLEM, Record
from .report import Report
from .versions import AddonVersion, KodiVersion


LOGGER = logging.getLogger(__name__)


def check_for_existing_addon(report: Report, addon_path: str, all_repo_addons: dict, pr: bool,
                             kodi_version: KodiVersion):
    """Check if addon submitted already exists or not
        :addon_path: path of the addon
        :all_repo_addons: dictionary return by all_repo_addon() function
    """

    addon_xml = os.path.join(addon_path, "addon.xml")
    addon_name, addon_version = _get_addon_name(addon_xml)
    addon_details = {'name': addon_name, 'version': addon_version}

    for branch, repo in sorted(all_repo_addons.items(), reverse=True):
        if KodiVersion(branch) <= kodi_version and addon_name in repo:
            _check_versions(report, addon_details, branch, repo.find(addon_name).version, pr)
            return

    report.add(Record(INFORMATION, "This is a new addon"))


def _get_addon_name(xml_path: str):
    """returns name and version of the addon
        :xml_path: path of the xml file
    """

    tree = ET.parse(xml_path).getroot()
    return (tree.get("id"), tree.get("version"))


def _check_versions(report: Report, addon_details, branch, repo_addons_version, pr):
    """Check for version bump in the existing addon

        :addon_details:       a dict containing name and version of the addon {'name': .., 'version': ..}
        :branch:              branch of the addon present in Kodi repository
        :repo_addons_version: version of addon present in Kodi repository
        :pr:                  boolean value indicating whether the check is
                              running on pull request or not
    """
    addon_name = addon_details.get('name')
    addon_version = addon_details.get('version')

    if pr:
        if AddonVersion(addon_version) > AddonVersion(repo_addons_version):
            LOGGER.info("%s addon have greater version: %s than repo_version: %s in branch %s",
                        addon_name, addon_version, repo_addons_version, branch)
        else:
            report.add(Record(PROBLEM, "%s addon already exists with a higher version: %s in %s branch"
                              % (addon_name, repo_addons_version, branch)))
    else:
        if AddonVersion(addon_version) < AddonVersion(repo_addons_version):
            report.add(Record(PROBLEM, "%s addon already exist with a higher version: %s in %s branch"
                              % (addon_name, repo_addons_version, branch)))
        else:
            report.add(Record(INFORMATION, "%s addon also exists in %s branch but with version: %s"
                              % (addon_name, branch, repo_addons_version)))
