"""
    Copyright (C) 2017-2018 Team Kodi
    This file is part of Kodi - kodi.tv

    SPDX-License-Identifier: GPL-3.0-only
    See LICENSES/README.md for more information.
"""

import os
import re
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from . import handle_files
from .common import relative_path
from .record import PROBLEM, Record, WARNING, INFORMATION
from .report import Report


def check_for_invalid_xml_files(report: Report, file_index: list):
    """check if any xml file present in the addon is invalid or not
        :file_index: A list having all the name and path of files in
                        addons
    """
    for file in file_index:
        if ".xml" in file["name"]:
            xml_path = os.path.join(file["path"], file["name"])
            try:
                # Just try if we can successfully parse it
                ET.parse(xml_path)
            except ET.ParseError:
                report.add(Record(PROBLEM, "Invalid xml found. %s" %
                                  relative_path(xml_path)))


def check_for_invalid_json_files(report: Report, file_index: list):
    """ check if any json file present in the addon is invalid or not
        :file_index: A list having all the name and path of files in
                     addons
    """
    for file in file_index:
        if ".json" in file["name"]:
            path = os.path.join(file["path"], file["name"])
            try:
                # Just try if we can successfully parse it
                with open(path) as json_data:
                    json.load(json_data)
            except ValueError:
                report.add(Record(PROBLEM, "Invalid json found. %s" %
                                  relative_path(path)))


def check_addon_xml(report: Report, addon_path: str, parsed_xml, folder_id_mismatch: bool):
    """Check whether the addon.xml present in the addon is parseable or not
        :addon_path: path to the addon
        :parsed_xml: parsed tree for xml file
        :folder_id_mismatch: whether to allow folder and id mismatch
    """
    addon_xml_path = os.path.join(addon_path, "addon.xml")
    try:
        handle_files.addon_file_exists(report, addon_path, r"addon\.xml")

        report.add(Record(INFORMATION, "Created by %s" %
                          parsed_xml.attrib.get("provider-name")))
        addon_xml_matches_folder(report, addon_path, parsed_xml, folder_id_mismatch)
    except ET.ParseError:
        report.add(Record(PROBLEM, "Addon xml not valid, check xml. %s" %
                          relative_path(addon_xml_path)))

    return parsed_xml


def addon_xml_matches_folder(report: Report, addon_path: str, parsed_xml, folder_id_mismatch: bool):
    """Check if the name of the addon matches the folder in which the addon
    files are present
        :addon_path: path to the addon folder
        :addon_xml: parsed tree for xml file
        :folder_id_mismatch: whether to allow folder and id mismatch
    """
    addon_id = parsed_xml.attrib.get("id")
    if os.path.basename(os.path.normpath(addon_path)) == addon_id:
        report.add(Record(INFORMATION, "Addon id matches folder name"))
    else:
        if folder_id_mismatch:
            report.add(Record(INFORMATION, "Addon id and folder name does not match. "
                                           "Ensure folder name is {} when submitting a PR "
                                           "to Kodi's official repository.".format(addon_id)))
        else:
            report.add(Record(PROBLEM, "Addon id and folder name does not match."))


def check_for_legacy_language_path(report: Report, addon_path: str):
    """Check whether the language directory structure is new or not
        :addon_path: path to addon folder
    """
    language_path = os.path.join(addon_path, "resources", "language")
    if os.path.exists(language_path):
        dirs = next(os.walk(language_path))[1]
        for directory in dirs:
            if "resource.language." not in directory:
                report.add(Record(
                    PROBLEM, "Using the old language directory structure, please move to the new one."))
                break


def check_file_whitelist(report: Report, file_index: list, addon_path: str,
                         whitelisted_files: list, whitelisted_exts: list):
    """check whether the files present in addon are in whitelist or not
        It ignores README.md and .gitignore file
        :file_index: list having names and path of all the files present in addon
        :addon_path: path to the addon folder
        :whitelisted_files: list of files/folders to whitelist provided by argument --exclude-file
        :whitelisted_exts: list of file extensions to whitelist provided by argument --exclude-file-ext
    """
    if ".module." in addon_path:
        report.add(Record(INFORMATION, "Module skipping whitelist"))
        return

    whitelisted_exts = "|".join(set([re.escape(ext.lstrip(".")) for ext in whitelisted_exts]))
    if whitelisted_exts:
        whitelisted_exts = "|" + whitelisted_exts

    whitelist = (
        r"\.?(py|xml|gif|png|jpg|jpeg|md|txt|po|json|gitignore|markdown|yml|"
        r"rst|ini|flv|wav|mp4|html|css|lst|pkla|g|template|in|cfg|xsd|directory|"
        r"help|list|mpeg|pls|info|ttf|xsp|theme|yaml|dict|crt{})?$".format(whitelisted_exts)
    )

    whitelisted_files = set(whitelisted_files)

    for file in file_index:
        full_path = os.path.join(file["path"], file["name"])
        if any(f == file["name"] or f == full_path or (os.path.isdir(f) and file["path"].startswith(f))
               for f in whitelisted_files):
            continue

        file_parts = file["name"].rsplit(".")
        if len(file_parts) > 1:
            file_ending = "." + file_parts[len(file_parts) - 1]
            if re.match(whitelist, file_ending, re.IGNORECASE) is None:
                report.add(Record(WARNING,
                                  "Found non whitelisted file ending in filename %s" %
                                  relative_path(os.path.join(file["path"], file["name"]))))


def check_file_permission(report: Report, file_index: list, whitelisted_files: list, whitelisted_exts: list):
    """Check whether the files present in addon are marked executable
       or not
        :file_index: list having names and path of all the files present in addon
        :whitelisted_files: list of files/folders to whitelist provided by argument --exclude-file
        :whitelisted_exts: list of file extensions to whitelist provided by argument --exclude-file-ext
    """

    whitelisted_exts = "|".join(set([re.escape(ext.lstrip(".")) for ext in whitelisted_exts]))
    whitelist = r"\.?({})?$".format(whitelisted_exts)

    whitelisted_files = set(whitelisted_files)

    for file in file_index:
        full_path = os.path.join(file["path"], file["name"])
        if any(f == file["name"] or f == full_path or (os.path.isdir(f) and file["path"].startswith(f))
               for f in whitelisted_files):
            continue

        if whitelisted_exts:
            file_parts = file["name"].rsplit(".")
            if len(file_parts) > 1:
                file_ending = "." + file_parts[len(file_parts) - 1]
                if re.match(whitelist, file_ending, re.IGNORECASE):
                    continue

        if os.path.isfile(full_path) and os.access(str(full_path), os.X_OK):
            report.add(Record(PROBLEM, "%s is marked as stand-alone executable" % relative_path(str(full_path))))
