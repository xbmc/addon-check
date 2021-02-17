"""
    Copyright (C) 2017-2018 Team Kodi
    This file is part of Kodi - kodi.tv

    SPDX-License-Identifier: GPL-3.0-only
    See LICENSES/README.md for more information.
"""

import logging
import os
import xml.etree.ElementTree as ET

from . import (check_artwork, check_dependencies, check_entrypoint,
               check_files, check_addon_branches, check_py3_compatibility,
               check_string, check_url, common, handle_files,
               schema_validation, ValidKodiVersions)
from .addons.Addon import Addon
from .addons.Repository import Repository
from .versions import KodiVersion
from .record import INFORMATION, Record
from .report import Report

ROOT_URL = "http://mirrors.kodi.tv/addons/{branch}/addons.xml.gz"
LOGGER = logging.getLogger(__name__)


def start(addon_path, args, all_repo_addons, config=None):
    """Starting point of all the checks that
       are to be performed on an addon

       :addon_path: Path to the addon that is to be checked
       :args: argparse object
       :all_repo_addons: a nested list having information
                         about all the repo addons
    """
    addon_id = os.path.basename(os.path.normpath(addon_path))
    addon_report = Report(addon_id)
    LOGGER.info("Checking add-on %s", addon_id)
    addon_report.add(Record(INFORMATION, "Checking add-on %s" % addon_id))

    repo_addons = all_repo_addons[args.branch]
    addon_xml_path = os.path.join(addon_path, "addon.xml")
    parsed_xml = ET.parse(addon_xml_path).getroot()

    # Extract common path from addon paths
    # All paths will be printed relative to this path
    common.REL_PATH = os.path.split(addon_path[:-1])[0]
    addon_xml = check_files.check_addon_xml(addon_report, addon_path, parsed_xml, args.allow_folder_id_mismatch)

    if addon_xml is not None:
        check_addon_branches.check_for_existing_addon(addon_report, Addon(parsed_xml), all_repo_addons, args)

        if not addon_xml.findall("*//broken") and \
           not (addon_xml.findall("*//lifecyclestate") and \
                addon_xml.find("*//lifecyclestate").attrib.get("type") == "broken"):
            file_index = handle_files.create_file_index(addon_path)

            schema_validation.schemas(addon_report, parsed_xml, args.branch)

            check_url.check_url(addon_report, parsed_xml)

            check_dependencies.check_addon_dependencies(addon_report, repo_addons, parsed_xml, args)

            check_dependencies.check_reverse_dependencies(addon_report, addon_id, args.branch, all_repo_addons)

            check_files.check_file_permission(addon_report, file_index)

            check_files.check_for_invalid_xml_files(addon_report, file_index)

            check_files.check_for_invalid_json_files(addon_report, file_index)

            check_artwork.check_artwork(addon_report, addon_path, parsed_xml, file_index, KodiVersion(args.branch))

            max_entrypoint_count = config.configs.get(
                "max_entrypoint_count", 15)
            check_entrypoint.check_complex_addon_entrypoint(
                addon_report, addon_path, parsed_xml, max_entrypoint_count)

            check_py3_compatibility.check_py3_compatibility(addon_report, addon_path, KodiVersion(args.branch))

            if config.is_enabled("check_license_file_exists"):
                # check if license file is existing
                handle_files.addon_file_exists(addon_report, addon_path,
                                               r"^LICENSE\.txt|LICENSE\.md|LICENSE$")

            check_string.check_for_legacy_strings_xml(addon_report, addon_path)

            if KodiVersion(args.branch) >= KodiVersion("isengard"):
                check_files.check_for_new_language_directory_structure(addon_report, addon_path)
            else:
                check_files.check_for_new_language_directory_structure(addon_report, addon_path, supported=False)

            check_string.check_for_invalid_strings_po(addon_report, file_index, addon_path)

            # Kodi 18 Leia + deprecations
            if config.is_enabled("check_kodi_leia_deprecations"):
                check_string.find_blacklisted_strings(addon_report, addon_path,
                                                      ["System.HasModalDialog", "StringCompare", "SubString",
                                                       "IntegerGreaterThan", "ListItem.ChannelNumber",
                                                       "ListItem.SubChannelNumber", "MusicPlayer.ChannelNumber",
                                                       "MusicPlayer.SubChannelNumber", "VideoPlayer.ChannelNumber",
                                                       "VideoPlayer.SubChannelNumber"],
                                                      [], [".py", ".xml"])

            # General blacklist
            check_string.find_blacklisted_strings(addon_report, addon_path, [], [], [])

            check_files.check_file_whitelist(addon_report, file_index, addon_path)
        else:
            addon_report.add(
                Record(INFORMATION, "Addon marked as broken - skipping"))

    return addon_report


def get_all_repo_addons():
    """Returns a nested dictionary of format:
        {'gotham':{'name_of_addon':'version_of_addon'}}
    """

    repo_addons = {}

    for branch in ValidKodiVersions:
        branch_url = ROOT_URL.format(branch=branch)
        repo_addons[branch] = Repository(branch, branch_url)

    return repo_addons
