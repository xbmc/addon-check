"""
    Copyright (C) 2017-2018 Team Kodi
    This file is part of Kodi - kodi.tv

    SPDX-License-Identifier: GPL-3.0-only
    See LICENSES/README.md for more information.
"""

import logging
import os
import xml.etree.ElementTree as ET

from .check_dependencies import VERSION_ATTRB
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

    is_new_addon = True
    for branch, repo in sorted(all_repo_addons.items(), reverse=True):

        # Addon submission must be higher than the versions already available in lower
        # branches to allow users to receive the update (especially if run with --pr)
        if KodiVersion(branch) <= kodi_version and addon_name in repo:
            is_new_addon = False
            _check_version_higher(report, addon_details, branch, repo.find(addon_name).version, pr)

        # Addon submission must be lower than the versions already available in upper repo branches
        # if that branch corresponds to a breaking change (e.g. version of addon in matrix version >
        # version of addon in gotham) since xbmc.python is not backwards compatible.
        elif KodiVersion(branch) > kodi_version and addon_name in repo and \
            not _is_pythonabi_compatible(repr(kodi_version), branch):
            is_new_addon = False
            _check_version_lower(report, addon_details, branch, repo.find(addon_name).version, pr)

    if is_new_addon:
        report.add(Record(INFORMATION, "This is a new addon"))


def _get_addon_name(xml_path: str):
    """returns name and version of the addon
        :xml_path: path of the xml file
    """

    tree = ET.parse(xml_path).getroot()
    return (tree.get("id"), tree.get("version"))


def _is_pythonabi_compatible(target_branch, upper_branch):
    """returns true if the target_branch for this addon is backwards compatible with a
        given upper branch. E.g. if kodi isengard python abi is comaptible with leia python abi.
        :target_branch: the branch the addon lives in (or is being PR'd to)
        : upper_branch: an upper branch that also contains an addon with the same addon id
    """
    return VERSION_ATTRB['xbmc.python'][upper_branch]["min_compatible"] == \
        VERSION_ATTRB['xbmc.python'][target_branch]["min_compatible"]


def _check_version_higher(report: Report, addon_details, branch, repo_addons_version, pr):
    """Check the version in lower branch is lower than the addon version being submitted
       thus allowing for addon updates.

        :addon_details:       a dict containing name and version of the addon {'name': .., 'version': ..}
        :branch:              branch of the addon present in Kodi repository
        :repo_addons_version: version of addon present in Kodi repository
        :pr:                  boolean value indicating whether the check is
                              running on pull request or not
    """
    addon_name = addon_details.get('name')
    addon_version = addon_details.get('version')

    if AddonVersion(addon_version) < AddonVersion(repo_addons_version) or \
        (AddonVersion(addon_version) == AddonVersion(repo_addons_version) and pr):
        report.add(
            Record(
                PROBLEM,
                "%s addon already exists with a higher or equal version: %s in %s branch. Users in %s won't " \
                "be able to receive the addon update."
                % (addon_name, repo_addons_version, branch, branch)
            )
        )
    else:
        if pr:
            report.add(Record(INFORMATION, "%s addon also exists in %s branch but with update compatible version: %s"
                              % (addon_name, branch, repo_addons_version)))



def _check_version_lower(report: Report, addon_details, branch, repo_addons_version, pr):
    """Check the version in upper branch is higher than the addon version being submitted
       thus allowing for kodi migration and inherent addon update.

        :addon_details:       a dict containing name and version of the addon {'name': .., 'version': ..}
        :branch:              branch of the addon present in Kodi repository
        :repo_addons_version: version of addon present in Kodi repository
        :pr:                  boolean value indicating whether the check is
                              running on pull request or not
    """
    addon_name = addon_details.get('name')
    addon_version = addon_details.get('version')

    if AddonVersion(addon_version) > AddonVersion(repo_addons_version) or \
        (AddonVersion(addon_version) == AddonVersion(repo_addons_version) and pr):
        report.add(
            Record(
                PROBLEM,
                "%s addon already exists with a lower or equal version: %s in %s branch. Users migrating " \
                "to kodi version %s won't be able to receive the addon update"
                % (addon_name, repo_addons_version, branch, branch)
            )
        )
    else:
        if pr:
            report.add(Record(INFORMATION, "%s addon also exists in %s branch but with migration compatible version: %s"
                              % (addon_name, branch, repo_addons_version)))
