"""
    Copyright (C) 2017-2018 Team Kodi
    This file is part of Kodi - kodi.tv

    SPDX-License-Identifier: GPL-3.0-only
    See LICENSES/README.md for more information.
"""

import os
import xml.etree.ElementTree as ET
import logging

from .addons.Repository import Repository
from .record import Record, INFORMATION
from .report import Report
from . import check_artwork
from . import check_old_addon
from . import check_dependencies
from . import check_entrypoint
from . import handle_files
from . import check_files
from . import check_string
from . import check_py3_compatibility
from . import check_url
from . import common
from . import schema_validation

ROOT_URL = "http://mirrors.kodi.tv/addons/{branch}/addons.xml.gz"
LOGGER = logging.getLogger(__name__)


def start(addon_path, args, all_repo_addons, config=None):
    addon_id = os.path.basename(os.path.normpath(addon_path))
    addon_report = Report(addon_id)
    LOGGER.info("Checking add-on %s" % addon_id)
    addon_report.add(Record(INFORMATION, "Checking add-on %s" % addon_id))

    repo_addons = all_repo_addons[args.branch]
    addon_xml_path = os.path.join(addon_path, "addon.xml")
    parsed_xml = ET.parse(addon_xml_path).getroot()

    # Extract common path from addon paths
    # All paths will be printed relative to this path
    common.REL_PATH = os.path.split(addon_path[:-1])[0]
    addon_xml = check_files.check_addon_xml(addon_report, addon_path, parsed_xml, args.allow_folder_id_mismatch)

    if addon_xml is not None:
        check_old_addon.check_for_existing_addon(addon_report, addon_path, all_repo_addons, args.PR)

        if len(addon_xml.findall("*//broken")) == 0:
            file_index = handle_files.create_file_index(addon_path)

            schema_validation.schemas(addon_report, parsed_xml, args.branch)

            check_url.check_url(addon_report, parsed_xml)

            check_dependencies.check_addon_dependencies(addon_report, repo_addons, parsed_xml, args.branch)

            check_dependencies.check_reverse_dependencies(addon_report, addon_id, args.branch, all_repo_addons)

            check_files.check_file_permission(addon_report, file_index)

            check_files.check_for_invalid_xml_files(addon_report, file_index)

            check_files.check_for_invalid_json_files(addon_report, file_index)

            check_artwork.check_artwork(addon_report, addon_path, parsed_xml, file_index)

            max_entrypoint_count = config.configs.get(
                "max_entrypoint_count", 15)
            check_entrypoint.check_complex_addon_entrypoint(
                addon_report, addon_path, parsed_xml, max_entrypoint_count)

            check_py3_compatibility.check_py3_compatibility(addon_report, addon_path, args.branch)

            if config.is_enabled("check_license_file_exists"):
                # check if license file is existing
                handle_files.addon_file_exists(addon_report, addon_path,
                                               r"^LICENSE\.txt|LICENSE\.md|LICENSE$")

            check_string.check_for_legacy_strings_xml(addon_report, addon_path)

            if args.branch not in ['gotham', 'helix']:
                check_files.check_for_legacy_language_path(addon_report, addon_path)

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


def all_repo_addons():
    """Returns a nested dictionary of format:
        {'gotham':{'name_of_addon':'version_of_addon'}}
    """

    branches = ['gotham', 'helix', 'isengard', 'jarvis', 'krypton', 'leia']
    repo_addons = {}

    for branch in branches:
        branch_url = ROOT_URL.format(branch=branch)
        repo_addons[branch] = Repository(branch, branch_url)

    return repo_addons
