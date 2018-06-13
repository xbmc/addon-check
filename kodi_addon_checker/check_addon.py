import json
import os
import pathlib
import re
from distutils.version import LooseVersion
import xml.etree.ElementTree as ET
import requests
import logging
from kodi_addon_checker import logger
import gzip
from io import BytesIO

from kodi_addon_checker.common import relative_path
from kodi_addon_checker.record import PROBLEM, Record, WARNING, INFORMATION
from kodi_addon_checker.report import Report
from kodi_addon_checker import check_artwork
from kodi_addon_checker import check_dependencies
from kodi_addon_checker import check_entrypoint

REL_PATH = ""
ROOT_URL = "http://mirrors.kodi.tv/addons/{branch}/addons.xml.gz"
LOGGER = logging.getLogger(__name__)


def _find_file(name, path):
    for file_name in os.listdir(path):
        match = re.match(name, file_name, re.IGNORECASE)
        if match is not None:
            return os.path.join(path, match.string)
    return


# this looks for a file but only returns the first occurance
def _find_file_recursive(name, path):
    for file in os.walk(path):
        if name in file[2]:
            return os.path.join(path, name)
    return


def _create_file_index(path):
    file_index = []
    for dirs in os.walk(path):
        for file_name in dirs[2]:
            file_index.append({"path": dirs[0], "name": file_name})
    return file_index


def _find_in_file(path, search_terms, whitelisted_file_types):
    results = []
    if len(search_terms) > 0:
        for directory in os.walk(path):
            for file_name in directory[2]:
                if pathlib.Path(file_name).suffix in whitelisted_file_types or len(whitelisted_file_types) == 0:
                    file_path = os.path.join(directory[0], file_name)

                    searchfile = open(file_path, "r", encoding="utf8")
                    linenumber = 0
                    for line in searchfile:
                        linenumber = linenumber + 1
                        for term in search_terms:
                            if term in line:
                                results.append({"term": term, "line": line.strip(
                                ), "searchfile": file_path, "linenumber": linenumber})
                    searchfile.close()
    return results


def start(addon_path, branch_name, all_repo_addons, pr, config=None):
    addon_id = os.path.basename(os.path.normpath(addon_path))
    addon_report = Report(addon_id)
    LOGGER.info("Checking add-on %s" % addon_id)
    addon_report.add(Record(INFORMATION, "Checking add-on %s" % addon_id))

    repo_addons = all_repo_addons[branch_name]
    addon_xml_path = os.path.join(addon_path, "addon.xml")
    parsed_xml = ET.parse(addon_xml_path).getroot()

    global REL_PATH
    # Extract common path from addon paths
    # All paths will be printed relative to this path
    REL_PATH = os.path.split(addon_path[:-1])[0]
    addon_xml = _check_addon_xml(addon_report, addon_path, parsed_xml)

    if addon_xml is not None:
        if len(addon_xml.findall("*//broken")) == 0:
            file_index = _create_file_index(addon_path)

            check_dependencies.check_addon_dependencies(addon_report, repo_addons, parsed_xml)

            _check_for_invalid_xml_files(addon_report, file_index)

            _check_for_existing_addon(addon_report, addon_path, all_repo_addons, pr)

            _check_for_invalid_json_files(addon_report, file_index)

            check_artwork.check_artwork(addon_report, addon_path, parsed_xml, file_index)

            max_entrypoint_count = config.configs.get(
                "max_entrypoint_count", 15)
            check_entrypoint.check_complex_addon_entrypoint(
                addon_report, addon_path, parsed_xml, max_entrypoint_count)

            if config.is_enabled("check_license_file_exists"):
                # check if license file is existing
                _addon_file_exists(addon_report, addon_path,
                                   r"^LICENSE\.txt|LICENSE\.md|LICENSE$")

            if config.is_enabled("check_legacy_strings_xml"):
                _check_for_legacy_strings_xml(addon_report, addon_path)

            if config.is_enabled("check_legacy_language_path"):
                _check_for_legacy_language_path(addon_report, addon_path)

            # Kodi 18 Leia + deprecations
            if config.is_enabled("check_kodi_leia_deprecations"):
                _find_blacklisted_strings(addon_report, addon_path,
                                          ["System.HasModalDialog", "StringCompare", "SubString", "IntegerGreaterThan",
                                           "ListItem.ChannelNumber", "ListItem.SubChannelNumber",
                                           "MusicPlayer.ChannelNumber",
                                           "MusicPlayer.SubChannelNumber", "VideoPlayer.ChannelNumber",
                                           "VideoPlayer.SubChannelNumber"],
                                          [], [".py", ".xml"])

            # General blacklist
            _find_blacklisted_strings(addon_report, addon_path, [], [], [])

            _check_file_whitelist(addon_report, file_index, addon_path)
        else:
            addon_report.add(
                Record(INFORMATION, "Addon marked as broken - skipping"))

    return addon_report


def _check_for_invalid_xml_files(report: Report, file_index):
    for file in file_index:
        if ".xml" in file["name"]:
            xml_path = os.path.join(file["path"], file["name"])
            try:
                # Just try if we can successfully parse it
                ET.parse(xml_path)
            except ET.ParseError:
                report.add(Record(PROBLEM, "Invalid xml found. %s" %
                                  relative_path(xml_path)))


def _check_for_invalid_json_files(report: Report, file_index):
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


def _check_addon_xml(report: Report, addon_path, parsed_xml):
    addon_xml_path = os.path.join(addon_path, "addon.xml")
    try:
        _addon_file_exists(report, addon_path, r"addon\.xml")

        report.add(Record(INFORMATION, "Created by %s" %
                          parsed_xml.attrib.get("provider-name")))
        _addon_xml_matches_folder(report, addon_path, parsed_xml)
    except ET.ParseError:
        report.add(Record(PROBLEM, "Addon xml not valid, check xml. %s" %
                          relative_path(addon_xml_path)))

    return parsed_xml


def _addon_file_exists(report: Report, addon_path, file_name):
    if _find_file(file_name, addon_path) is None:
        report.add(Record(PROBLEM, "Not found %s in folder %s" %
                          (file_name, relative_path(addon_path))))


def _addon_xml_matches_folder(report: Report, addon_path, addon_xml):
    if os.path.basename(os.path.normpath(addon_path)) == addon_xml.attrib.get("id"):
        report.add(Record(INFORMATION, "Addon id matches folder name"))
    else:
        report.add(Record(PROBLEM, "Addon id and folder name does not match."))


def _check_for_legacy_strings_xml(report: Report, addon_path):
    if _find_file_recursive("strings.xml", addon_path) is not None:
        report.add(
            Record(PROBLEM, "Found strings.xml in folder %s please migrate to strings.po." % relative_path(addon_path)))


def _find_blacklisted_strings(report: Report, addon_path, problem_list, warning_list, whitelisted_file_types):
    for result in _find_in_file(addon_path, problem_list, whitelisted_file_types):
        report.add(Record(PROBLEM, "Found blacklisted term %s in file %s:%s (%s)"
                          % (result["term"], result["searchfile"], result["linenumber"], result["line"])))

    for result in _find_in_file(addon_path, warning_list, whitelisted_file_types):
        report.add(Record(WARNING, "Found blacklisted term %s in file %s:%s (%s)"
                          % (result["term"], result["searchfile"], result["linenumber"], result["line"])))


def _check_for_legacy_language_path(report: Report, addon_path):
    language_path = os.path.join(addon_path, "resources", "language")
    if os.path.exists(language_path):
        dirs = next(os.walk(language_path))[1]
        found_warning = False
        for dir in dirs:
            if not found_warning and "resource.language." not in dir:
                report.add(Record(
                    WARNING, "Using the old language directory structure, please move to the new one."))
                found_warning = True


def _check_file_whitelist(report: Report, file_index, addon_path):
    if ".module." in addon_path:
        report.add(Record(INFORMATION, "Module skipping whitelist"))
        return

    whitelist = (
        r"\.?(py|xml|gif|png|jpg|jpeg|md|txt|po|json|gitignore|markdown|yml|"
        r"rst|ini|flv|wav|mp4|html|css|lst|pkla|g|template|in|cfg|xsd|directory|"
        r"help|list|mpeg|pls|info|ttf|xsp|theme|yaml|dict|crt)?$"
    )

    for file in file_index:
        file_parts = file["name"].rsplit(".")
        # Only check file endings if there are file endings...
        # This will not check "README" or ".gitignore"
        if len(file_parts) > 1:
            file_ending = "." + file_parts[len(file_parts) - 1]
            if re.match(whitelist, file_ending, re.IGNORECASE) is None:
                report.add(Record(WARNING,
                                  "Found non whitelisted file ending in filename %s" %
                                  relative_path(os.path.join(file["path"], file["name"]))))


def _get_addons(xml_url):
    """addon.xml for the target Kodi version"""
    try:
        gz_file = requests.get(xml_url, timeout=(10, 10)).content
        with gzip.open(BytesIO(gz_file), 'rb') as xml_file:
            content = xml_file.read()
        tree = ET.fromstring(content)

        return {
            a.get("id"): a.get("version")
            for a in tree.findall("addon")
        }
    except requests.exceptions.ReadTimeout as errrt:
        LOGGER.error(errrt)
    except requests.exceptions.ConnectTimeout as errct:
        LOGGER.error(errct)


def _get_addon_name(xml_path):
    tree = ET.parse(xml_path).getroot()
    return (tree.get("id"), tree.get("version"))


def _check_for_existing_addon(report: Report, addon_path, all_repo_addons, pr):
    """Check if addon submitted already exists or not"""
    addon_xml = os.path.join(addon_path, "addon.xml")
    addon_name, addon_version = _get_addon_name(addon_xml)

    for branch in sorted(all_repo_addons):
        repo_addons = all_repo_addons[branch]

        if addon_name in repo_addons:
            _check_versions(report, addon_name, branch, addon_version, repo_addons[addon_name], pr)
            return

    report.add(Record(INFORMATION, "This is a new addon"))


def _check_versions(report: Report, addon_name, branch, addon_version, repo_addons_version, pr):
    if pr:
        if LooseVersion(addon_version) > LooseVersion(repo_addons_version):
            LOGGER.info("%s addon have greater version: %s than repo_version: %s in branch %s"
                        % (addon_name, addon_version, repo_addons_version, branch))
        else:
            report.add(Record(PROBLEM, "%s addon already exists with version: %s in %s branch")
                       % (addon_name, repo_addons_version, branch))
    else:
        if LooseVersion(addon_version) < LooseVersion(repo_addons_version):
            report.add(Record(PROBLEM, "%s addon already exist with version: %s in %s branch"
                              % (addon_name, repo_addons_version, branch)))
        else:
            report.add(Record(INFORMATION, "%s addon also exists in %s branch but with version: %s"
                              % (addon_name, branch, repo_addons_version)))


def all_repo_addons():
    branches = ['gotham', 'helix', 'isengard', 'jarvis', 'krypton', 'leia']
    repo_addons = {}

    for branch in branches:
        branch_url = ROOT_URL.format(branch=branch)
        repo_addons[branch] = _get_addons(branch_url)

    return repo_addons
