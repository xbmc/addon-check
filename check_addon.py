import json
import os
import pathlib
import re
import xml.etree.ElementTree

from PIL import Image

from common import colorPrint, check_config, has_transparency

REL_PATH = ""
comments_problem = []
comments_warning = []


def _find_file(name, path):
    for file_name in os.listdir(path):
        match = re.match(name, file_name, re.IGNORECASE)
        if match is not None:
            return os.path.join(path, match.string)
    return


# this looks for a file but only returns the first occurrence
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


def start(error_counter, addon_path, config=None):
    colorPrint("Checking %s" % os.path.basename(
        os.path.normpath(addon_path)), "34")

    global REL_PATH
    # Extract common path from addon paths
    # All paths will be printed relative to this path
    REL_PATH = os.path.split(addon_path[:-1])[0]
    error_counter, addon_xml = _check_addon_xml(error_counter, addon_path)

    if addon_xml is not None:
        if len(addon_xml.findall("*//broken")) == 0:
            file_index = _create_file_index(addon_path)

            error_counter = _check_for_invalid_xml_files(
                error_counter, file_index)

            error_counter = _check_for_invalid_json_files(
                error_counter, file_index)

            error_counter = _check_artwork(
                error_counter, addon_path, addon_xml, file_index)

            if check_config(config, "check_license_file_exists"):
                # check if license file is existing
                error_counter = _addon_file_exists(
                    error_counter, addon_path, "LICENSE\.txt|LICENSE\.md|LICENSE")

            if check_config(config, "check_legacy_strings_xml"):
                error_counter = _check_for_legacy_strings_xml(
                    error_counter, addon_path)

            if check_config(config, "check_legacy_language_path"):
                error_counter = _check_for_legacy_language_path(
                    error_counter, addon_path)

            # Kodi 18 Leia + deprecations
            if check_config(config, "check_kodi_leia_deprecations"):
                error_counter = _find_blacklisted_strings(
                    error_counter, addon_path,
                    ["System.HasModalDialog", "StringCompare", "SubString", "IntegerGreaterThan",
                     "ListItem.ChannelNumber", "ListItem.SubChannelNumber", "MusicPlayer.ChannelNumber",
                     "MusicPlayer.SubChannelNumber", "VideoPlayer.ChannelNumber", "VideoPlayer.SubChannelNumber"],
                    [], [".py", ".xml"])

            # General blacklist
            error_counter = _find_blacklisted_strings(
                error_counter, addon_path, [], [], [])

            error_counter = _check_file_whitelist(
                error_counter, file_index, addon_path)
        else:
            print("Addon marked as broken - skipping")

    return error_counter


def _check_for_invalid_xml_files(error_counter, file_index):
    for file in file_index:
        if ".xml" in file["name"]:
            xml_path = os.path.join(file["path"], file["name"])
            try:
                # Just try if we can successfully parse it
                xml.etree.ElementTree.parse(xml_path)
            except xml.etree.ElementTree.ParseError:
                error_counter = _logProblem(
                    error_counter, "Invalid xml found. %s" % relative_path(xml_path))

    return error_counter


def _check_for_invalid_json_files(error_counter, file_index):
    for file in file_index:
        if ".json" in file["name"]:
            path = os.path.join(file["path"], file["name"])
            try:
                # Just try if we can successfully parse it
                with open(path) as json_data:
                    json.load(json_data)
            except ValueError:
                error_counter = _logProblem(
                    error_counter, "Invalid json found. %s" % relative_path(path))

    return error_counter


def _check_addon_xml(error_counter, addon_path):
    addon_xml_path = os.path.join(addon_path, "addon.xml")
    addon_xml = None
    try:
        error_counter = _addon_file_exists(
            error_counter, addon_path, "addon\.xml")

        addon_xml = xml.etree.ElementTree.parse(addon_xml_path)
        addon = addon_xml.getroot()
        colorPrint("created by %s" % addon.attrib.get("provider-name"), "34")
        error_counter = _addon_xml_matches_folder(
            error_counter, addon_path, addon_xml)
    except xml.etree.ElementTree.ParseError:
        error_counter = _logProblem(
            error_counter, "Addon xml not valid, check xml. %s" % relative_path(addon_xml_path))

    return error_counter, addon_xml


def _check_artwork(error_counter, addon_path, addon_xml, file_index):
    # icon, fanart, screenshot - these will also check if the addon.xml links correctly
    error_counter = _check_image_type(
        error_counter, "icon", addon_xml, addon_path)
    error_counter = _check_image_type(
        error_counter, "fanart", addon_xml, addon_path)
    error_counter = _check_image_type(
        error_counter, "screenshot", addon_xml, addon_path)

    # go through all but the above and try to open the image
    for file in file_index:
        if re.match("(?!fanart\.jpg|icon\.png).*\.(png|jpg|jpeg|gif)$", file["name"]) is not None:
            image_path = os.path.join(file["path"], file["name"])
            try:
                # Just try if we can successfully open it
                Image.open(image_path)
            except IOError:
                error_counter = _logProblem(
                    error_counter, "Could not open image, is the file corrupted? %s" % relative_path(image_path))

    return error_counter


def _check_image_type(error_counter, image_type, addon_xml, addon_path):
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
                print("Image %s exists" % image_type)
                try:
                    im = Image.open(filepath)
                    width, height = im.size

                    if image_type == "icon":
                        if has_transparency(im):
                            error_counter = _logProblem(
                                error_counter, "Icon.png should be solid. It has transparency.")
                        if (width != 256 and height != 256) and (width != 512 and height != 512):
                            error_counter = _logProblem(
                                error_counter,
                                "Icon should have either 256x256 or 512x512 but it has %sx%s" % (width, height))
                        else:
                            print("%s dimensions are fine %sx%s" %
                                  (image_type, width, height))
                    elif image_type == "fanart":
                        fanart_sizes = [
                            (1280, 720), (1920, 1080), (3840, 2160)]
                        fanart_sizes_str = " or ".join(
                            ["%dx%d" % (w, h) for w, h in fanart_sizes])
                        if (width, height) not in fanart_sizes:
                            error_counter = _logProblem(
                                error_counter,
                                "Fanart should have either %s but it has %sx%s" % (fanart_sizes_str, width, height))
                        else:
                            print("%s dimensions are fine %sx%s" %
                                  (image_type, width, height))
                    else:
                        # screenshots have no size definitions
                        pass
                except IOError:
                    error_counter = _logProblem(
                        error_counter, "Could not open image, is the file corrupted? %s" % relative_path(filepath))

            else:
                # if it's a fallback path addons.xml should still be able to
                # get build
                if fanart_fallback or icon_fallback:
                    if icon_fallback:
                        print("You might want to add a icon")
                    elif fanart_fallback:
                        print("You might want to add a fanart")
                # it's no fallback path, so building addons.xml will crash -
                # this is a problem ;)
                else:
                    error_counter = _logProblem(
                        error_counter, "%s does not exist at specified path." % image_type)
        else:
            error_counter = _logWarning(
                error_counter, "Empty image tag found for %s" % image_type)
    return error_counter


def _addon_file_exists(error_counter, addon_path, file_name):
    if _find_file(file_name, addon_path) is None:
        return _logProblem(error_counter, "Not found %s in folder %s" % (file_name, relative_path(addon_path)))
    else:
        return error_counter


def _addon_xml_matches_folder(error_counter, addon_path, addon_xml):
    addon = addon_xml.getroot()
    if os.path.basename(os.path.normpath(addon_path)) == addon.attrib.get("id"):
        print("Addon id matches foldername")
    else:
        error_counter = _logProblem(
            error_counter, "Addon id and foldername does not match.")
    return error_counter


def _check_for_legacy_strings_xml(error_counter, addon_path):
    if _find_file_recursive("strings.xml", addon_path) is None:
        return error_counter
    else:
        return _logProblem(error_counter,
                           "Found strings.xml in folder %s please migrate to strings.po." % relative_path(addon_path))


def _find_blacklisted_strings(error_counter, addon_path, problem_list, warning_list, whitelisted_file_types):
    for result in _find_in_file(addon_path, problem_list, whitelisted_file_types):
        error_counter = _logProblem(error_counter, "Found blacklisted term %s in file %s:%s (%s)"
                                    % (result["term"], result["searchfile"],
                                       result["linenumber"], result["line"]))

    for result in _find_in_file(addon_path, warning_list, whitelisted_file_types):
        error_counter = _logWarning(error_counter, "Found blacklisted term %s in file %s:%s (%s)"
                                    % (result["term"], result["searchfile"],
                                       result["linenumber"], result["line"]))

    return error_counter


def _check_for_legacy_language_path(error_counter, addon_path):
    language_path = os.path.join(addon_path, "resources", "language")
    if os.path.exists(language_path):
        dirs = next(os.walk(language_path))[1]
        found_warning = False
        for dir in dirs:
            if not found_warning and "resource.language." not in dir:
                error_counter = _logWarning(
                    error_counter, "Using the old language directory structure, please move to the new one.")
                found_warning = True
    return error_counter


def _check_file_whitelist(error_counter, file_index, addon_path):
    if ".module." in addon_path:
        print("Module skipping whitelist")
        return error_counter

    whitelist = r"\.?(py|xml|gif|png|jpg|jpeg|md|txt|po|json|gitignore|markdown|yml|rst|ini|flv|wav|mp4|html|css|lst|pkla|g|template|in|cfg|xsd|directory|help|list|mpeg|pls|info|ttf|xsp|theme|yaml|dict|crt)?$"

    for file in file_index:
        file_parts = file["name"].rsplit(".")
        # Only check file endings if there are file endings...
        # This will not check "README" or ".gitignore"
        if len(file_parts) > 1:
            file_ending = "." + file_parts[len(file_parts) - 1]
            if re.match(whitelist, file_ending, re.IGNORECASE) is None:
                error_counter = _logProblem(error_counter, "Found non whitelisted file ending in filename %s" % (
                    os.path.join(file["path"], file["name"])))

    return error_counter


def relative_path(file_path):
    path_to_print = file_path[len(REL_PATH):]
    return ".{}".format(path_to_print) 


def _logProblem(error_counter, problem_string):
    colorPrint("PROBLEM: %s" % problem_string, "31")
    comments_problem.append(problem_string)
    error_counter["problems"] = error_counter["problems"] + 1
    return error_counter


def _logWarning(error_counter, warning_string):
    colorPrint("WARNING: %s" % warning_string, "35")
    comments_warning.append(warning_string)
    error_counter["warnings"] = error_counter["warnings"] + 1
    return error_counter
