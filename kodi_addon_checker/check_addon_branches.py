"""
    Copyright (C) 2017-2018 Team Kodi
    This file is part of Kodi - kodi.tv

    SPDX-License-Identifier: GPL-3.0-only
    See LICENSES/README.md for more information.
"""

import logging
import xml.etree.ElementTree as ET

from .addons.Addon import Addon
from .check_dependencies import VERSION_ATTRB
from .record import INFORMATION, PROBLEM, Record, WARNING
from .report import Report
from .versions import AddonVersion, KodiVersion


LOGGER = logging.getLogger(__name__)


def check_for_existing_addon(report: Report, addon: Addon, all_repo_addons: dict, args):
    """Check if addon submitted already exists or not
        :report: the report object
        :addon: the Addon object (contains id and version)
        :all_repo_addons: dictionary return by all_repo_addon() function
        :args: the args object passed to addon-checker
    """
    # addon details
    addon_name = addon.id
    addon_version = addon.version
    addon_details = {'name': addon_name, 'version': addon_version}

    # args
    pr = bool(args.PR)
    kodi_version = KodiVersion(args.branch)

    is_new_addon = True
    for branch, repo in sorted(all_repo_addons.items(), reverse=True):

        # Addon submission must be higher than the versions already available in lower
        # branches to allow users to receive the update (especially if run with --pr)
        if KodiVersion(branch) <= kodi_version and addon_name in repo:
            is_new_addon = False
            _check_version_higher(report, addon_details, branch, repo.find(addon_name).version, pr)

        # Addon submission must be lower than the versions already available in upper repo branches
        # if that branch corresponds to a breaking change (e.g. version of addon in matrix version >
        # version of addon in gotham) since there might be dependencies not abi-backward compatible.
        elif KodiVersion(branch) > kodi_version and addon_name in repo and \
            not _is_xbmcabi_compatible(addon.dependencies, repr(kodi_version), branch):
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


def _is_xbmcabi_compatible(dependencies: list, target_branch: str, upper_branch: str):
    """returns true if the target_branch for this addon is backwards compatible with a
        given upper branch. E.g. if there are dependencies on the addon that are ABI incompatible
        with the migration to an upper kodi version (resulting in the addon being incompatible)
        :dependencies: the list of dependencies of the addon
        :target_branch: the branch the addon lives in (or is being PR'd to)
        :upper_branch: an upper branch that also contains an addon with the same addon id
    """
    for dependency in dependencies:
        if dependency.id in VERSION_ATTRB:
            if AddonVersion(VERSION_ATTRB[dependency.id][upper_branch]["min_compatible"]) > \
                AddonVersion(VERSION_ATTRB[dependency.id][target_branch]["min_compatible"]):
                return False
    return True


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

    if AddonVersion(addon_version) <= AddonVersion(repo_addons_version) and pr:
        report.add(
            Record(
                PROBLEM,
                f"{addon_name} addon already exists with a higher or equal version: {repo_addons_version} "\
                    f"in {branch} branch. Users in {branch} won't " \
                     "be able to receive the addon update."
            )
        )
    else:
        if pr:
            report.add(Record(INFORMATION,
            f"{addon_name} addon also exists in {branch} branch but " \
                f"with update compatible version: {repo_addons_version}"))


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
                PROBLEM if pr else WARNING,
                f"{addon_name} addon already exists with a lower or equal version: " \
                f"{repo_addons_version} in {branch} branch " \
                "and the addon has non forward abi compatible dependencies. Users migrating " \
                f"to kodi version {branch} won't be able to receive the addon update."
            )
        )
    else:
        if pr:
            report.add(Record(INFORMATION, f"{addon_name} addon also exists "\
                f"in {branch} branch but with migration compatible version: {repo_addons_version}"))
