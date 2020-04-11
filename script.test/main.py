"""
This file contain the code of addon checker tool.
This is done to increase the size of entry point file.
"""

from resources.lib import kodilogging
from resources.lib import script
import json
import os
import pathlib
import re
from radon.raw import analyze
import xml.etree.ElementTree as ET

from PIL import Image

from kodi_addon_checker.common import has_transparency
from kodi_addon_checker.record import PROBLEM, Record, WARNING, INFORMATION
from kodi_addon_checker.report import Report
from kodi_addon_checker.versions import AddonVersion

import logging
import xbmcaddon

ADDON = xbmcaddon.Addon()
kodilogging.config()

script.show_dialog()


REL_PATH = ""


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


def start(addon_path, repo_addons, config=None):
    addon_id = os.path.basename(os.path.normpath(addon_path))
    addon_report = Report(addon_id)
    addon_report.add(Record(INFORMATION, "Checking add-on %s" % addon_id))

    global REL_PATH
    # Extract common path from addon paths
    # All paths will be printed relative to this path
    REL_PATH = os.path.split(addon_path[:-1])[0]
    addon_xml = _check_addon_xml(addon_report, addon_path)

    if addon_xml is not None:
        if len(addon_xml.findall("*//broken")) == 0:
            file_index = _create_file_index(addon_path)

            _check_dependencies(addon_report, addon_path, repo_addons)

            _check_for_invalid_xml_files(addon_report, file_index)

            _check_for_invalid_json_files(addon_report, file_index)

            _check_artwork(addon_report, addon_path, addon_xml, file_index)

            max_entrypoint_line_count = config.configs.get("max_entrypoint_line_count", 15)
            _check_complex_addon_entrypoint(addon_report, addon_path, max_entrypoint_line_count)

            if config.is_enabled("check_license_file_exists"):
                # check if license file is existing
                _addon_file_exists(addon_report, addon_path, r"^LICENSE\.txt|LICENSE\.md|LICENSE$")

            _check_for_legacy_strings_xml(addon_report, addon_path)

            if branch_name not in ['gotham', 'helix']:
                check_for_new_language_directory_structure(addon_report, addon_path)
            else:
                check_for_new_language_directory_structure(addon_report, addon_path, supported=False)

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
            addon_report.add(Record(INFORMATION, "Addon marked as broken - skipping"))

    return addon_report


def _check_for_invalid_xml_files(report: Report, file_index):
    for file in file_index:
        if ".xml" in file["name"]:
            xml_path = os.path.join(file["path"], file["name"])
            try:
                # Just try if we can successfully parse it
                ET.parse(xml_path)
            except ET.ParseError:
                report.add(Record(PROBLEM, "Invalid xml found. %s" % relative_path(xml_path)))


def _check_for_invalid_json_files(report: Report, file_index):
    for file in file_index:
        if ".json" in file["name"]:
            path = os.path.join(file["path"], file["name"])
            try:
                # Just try if we can successfully parse it
                with open(path) as json_data:
                    json.load(json_data)
            except ValueError:
                report.add(Record(PROBLEM, "Invalid json found. %s" % relative_path(path)))


def _check_addon_xml(report: Report, addon_path):
    addon_xml_path = os.path.join(addon_path, "addon.xml")
    addon_xml = None
    try:
        _addon_file_exists(report, addon_path, r"addon\.xml")

        addon_xml = ET.parse(addon_xml_path)
        addon = addon_xml.getroot()
        report.add(Record(INFORMATION, "Created by %s" % addon.attrib.get("provider-name")))
        _addon_xml_matches_folder(report, addon_path, addon_xml)
    except ET.ParseError:
        report.add(Record(PROBLEM, "Addon xml not valid, check xml. %s" % relative_path(addon_xml_path)))

    return addon_xml


def _check_artwork(report: Report, addon_path, addon_xml, file_index):
    # icon, fanart, screenshot - these will also check if the addon.xml links correctly
    _check_image_type(report, "icon", addon_xml, addon_path)
    _check_image_type(report, "fanart", addon_xml, addon_path)
    _check_image_type(report, "screenshot", addon_xml, addon_path)

    # go through all but the above and try to open the image
    for file in file_index:
        if re.match(r"(?!fanart\.jpg|icon\.png).*\.(png|jpg|jpeg|gif)$", file["name"]) is not None:
            image_path = os.path.join(file["path"], file["name"])
            try:
                # Just try if we can successfully open it
                Image.open(image_path)
            except IOError:
                report.add(
                    Record(PROBLEM, "Could not open image, is the file corrupted? %s" % relative_path(image_path)))


def _check_image_type(report: Report, image_type, addon_xml, addon_path):
    images = addon_xml.findall("*//" + image_type)

    icon_fallback = False
    fanart_fallback = False
    if not images and image_type == "icon":
        icon_fallback = True
        image = type('image', (object,),
                     {'text': 'icon.png'})()
        images.append(image)
    elif not images and image_type == "fanart":
        skip_addon_types = [".module.", "metadata.", "context.", ".language."]
        for addon_type in skip_addon_types:
            if addon_type in addon_path:
                break
        else:
            fanart_fallback = True
            image = type('image', (object,),
                         {'text': 'fanart.jpg'})()
            images.append(image)

    for image in images:
        if image.text:
            filepath = os.path.join(addon_path, image.text)
            if os.path.isfile(filepath):
                report.add(Record(INFORMATION, "Image %s exists" % image_type))
                try:
                    im = Image.open(filepath)
                    width, height = im.size

                    if image_type == "icon":
                        if has_transparency(im):
                            report.add(Record(PROBLEM, "Icon.png should be solid. It has transparency."))
                        if (width != 256 and height != 256) and (width != 512 and height != 512):
                            report.add(Record(PROBLEM, "Icon should have either 256x256 or 512x512 but it has %sx%s" % (
                                width, height)))
                        else:
                            report.add(
                                Record(INFORMATION, "%s dimensions are fine %sx%s" % (image_type, width, height)))
                    elif image_type == "fanart":
                        fanart_sizes = [(1280, 720), (1920, 1080), (3840, 2160)]
                        fanart_sizes_str = " or ".join(["%dx%d" % (w, h) for w, h in fanart_sizes])
                        if (width, height) not in fanart_sizes:
                            report.add(Record(PROBLEM, "Fanart should have either %s but it has %sx%s" % (
                                fanart_sizes_str, width, height)))
                        else:
                            report.add(Record(INFORMATION, "%s dimensions are fine %sx%s" %
                                              (image_type, width, height)))
                    else:
                        # screenshots have no size definitions
                        pass
                except IOError:
                    report.add(
                        Record(PROBLEM, "Could not open image, is the file corrupted? %s" % relative_path(filepath)))

            else:
                # if it's a fallback path addons.xml should still be able to
                # get build
                if fanart_fallback or icon_fallback:
                    if icon_fallback:
                        report.add(Record(INFORMATION, "You might want to add a icon"))
                    elif fanart_fallback:
                        report.add(Record(INFORMATION, "You might want to add a fanart"))
                # it's no fallback path, so building addons.xml will crash -
                # this is a problem ;)
                else:
                    report.add(Record(PROBLEM, "%s does not exist at specified path." % image_type))
        else:
            report.add(Record(WARNING, "Empty image tag found for %s" % image_type))


def _addon_file_exists(report: Report, addon_path, file_name):
    if _find_file(file_name, addon_path) is None:
        report.add(Record(PROBLEM, "Not found %s in folder %s" % (file_name, relative_path(addon_path))))


def _addon_xml_matches_folder(report: Report, addon_path, addon_xml):
    addon = addon_xml.getroot()
    if os.path.basename(os.path.normpath(addon_path)) == addon.attrib.get("id"):
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


def check_for_new_language_directory_structure(report: Report, addon_path, supported=True):
    language_path = os.path.join(addon_path, "resources", "language")
    if os.path.exists(language_path):
        dirs = next(os.walk(language_path))[1]
        found_warning = False
        for directory in dirs:
            if not found_warning and "resource.language." not in directory and supported:
                report.add(Record(
                    WARNING, "Using the old language directory structure in %s, please move to the new one." %
                    os.path.join(language_path, directory)))
                found_warning = True
            elif not found_warning "resource.language." in directory and not supported:
                report.add(Record(
                    WARNING, "Using the new language directory structure in %s for a Kodi version that does not" \
                             "support it. Please use the old language file struture or move the addon to" \
                             "an upper branch/kodi version." % os.path.join(language_path, directory)))
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


def relative_path(file_path):
    path_to_print = file_path[len(REL_PATH):]
    return ".{}".format(path_to_print)


def _check_complex_addon_entrypoint(report: Report, addon_path, max_entrypoint_line_count):

    addon_xml_path = os.path.join(addon_path, "addon.xml")
    tree = ET.parse(addon_xml_path).getroot()

    for i in tree.findall("extension"):
        library = i.get("library")

        if library:
            filepath = os.path.join(addon_path, library)

            if not os.path.isdir(filepath):

                if os.path.exists(filepath):
                    lineno = number_of_lines(filepath)
                    if lineno >= max_entrypoint_line_count:
                        report.add(Record(WARNING,
                                          "Complex entry point. Check: %s | Counted lines: %d | Lines allowed: %d"
                                          % (library, lineno, max_entrypoint_line_count)))

                else:
                    report.add(Record(PROBLEM, "%s Entry point does not exists" % library))


def number_of_lines(filepath):
    with open(filepath, 'r') as file:
        data = file.read()

    return (analyze(data).lloc)


def _get_users_dependencies(addon_path):
    """
        User's addon.xml from pull request
    """
    addon_xml_path = os.path.join(addon_path, "addon.xml")

    tree = ET.parse(addon_xml_path).getroot()

    return {
        i.get("addon"): i.get("version")
        for i in tree.findall("requires/import")
    }


def _check_dependencies(report: Report, addon_path, repo_addons):
    deps = _get_users_dependencies(addon_path)
    ignore = ['xbmc.json', 'xbmc.gui', 'xbmc.json', 'xbmc.metadata', 'xbmc.python']

    for required_addon, required_version in deps.items():
        if required_addon not in repo_addons:
            if required_addon not in ignore:
                report.add(Record(PROBLEM, "Required addon %s not available in current repository." % required_addon))
        else:
            available_version = repo_addons[required_addon]

            if AddonVersion(available_version) < AddonVersion(required_version) and (required_addon not in ignore):
                report.add(Record(PROBLEM, "Version mismatch for addon %s. Required: %s, Available: %s "
                                  % (required_addon, required_version, available_version)))
