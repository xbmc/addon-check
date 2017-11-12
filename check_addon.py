import os
import re
import json
import xml.etree.ElementTree
from PIL import Image
from common import colorPrint


def _find_file(name, path):
    for file_name in os.listdir(path):
        match = re.match(name, file_name)
        if match != None:
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

def find_in_file(path, search_terms):
    results = []
    if len(search_terms) > 0:
        for dir in os.walk(path):
            for file_name in dir[2]:
                file_path = os.path.join(dir[0], file_name)
                searchfile = open(file_path, "r")
                linenumber = 0
                for line in searchfile:
                    linenumber = linenumber + 1
                    for term in search_terms:
                        if term in line:
                            results.append({"term": term, "line": line.strip(
                            ), "searchfile": file_path, "linenumber": linenumber})
                searchfile.close()
    return results

def _check_config(config, value):
    return config is None or config[value] is True

def start(error_counter, addon_path, config = None):
    colorPrint("Checking %s" % os.path.basename(
        os.path.normpath(addon_path)), "34")

    error_counter, addon_xml = _check_addon_xml(error_counter, addon_path)

    if addon_xml != None:
        if len(addon_xml.findall("*//broken")) == 0:
            file_index = _create_file_index(addon_path)

            error_counter = _check_for_invalid_xml_files(error_counter, file_index)

            error_counter = _check_for_invalid_json_files(
                error_counter, file_index)

            error_counter = _check_artwork(error_counter, addon_path, addon_xml, file_index)

            if _check_config(config, "check_license_file_exists"):
                # check if license file is existing
                error_counter = _addon_file_exists(error_counter, addon_path, "LICENSE\.txt|LICENSE\.md|LICENSE")

            if _check_config(config, "check_legacy_strings_xml"):
                error_counter = _check_for_legacy_strings_xml(error_counter, addon_path)

            if _check_config(config, "check_legacy_language_path"):
                error_counter = _check_for_legacy_language_path(error_counter, addon_path)

            error_counter = _find_blacklisted_strings(error_counter, addon_path)

            error_counter = _check_file_whitelist(error_counter, file_index, addon_path)
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
                error_counter = _logProblem(error_counter, "Invalid xml found. %s" % xml_path)

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
                    error_counter, "Invalid json found. %s" % path)

    return error_counter


def _check_addon_xml(error_counter, addon_path):
    addon_xml_path = os.path.join(addon_path, "addon.xml")
    addon_xml = None
    try:
        error_counter = _addon_file_exists(error_counter, addon_path, "addon\.xml")

        addon_xml = xml.etree.ElementTree.parse(addon_xml_path)
        addon = addon_xml.getroot()
        colorPrint ("created by %s" % addon.attrib.get("provider-name"), "34")
        error_counter = _addon_xml_matches_folder(error_counter, addon_path, addon_xml)
    except xml.etree.ElementTree.ParseError:
        error_counter = _logProblem(error_counter, "Addon xml not valid, check xml. %s" % addon_xml_path)
    return error_counter, addon_xml


def _check_artwork(error_counter, addon_path, addon_xml, file_index):
    # icon, fanart, screenshot - these will also check if the addon.xml links correctly
    error_counter = _check_image_type(error_counter, "icon", addon_xml, addon_path)
    error_counter = _check_image_type(error_counter, "fanart", addon_xml, addon_path)
    error_counter = _check_image_type(error_counter, "screenshot", addon_xml, addon_path)

    # go through all but the above and try to open the image
    for file in file_index:
        if re.match("(?!fanart\.jpg|icon\.png).*\.(png|jpg|jpeg|gif)$", file["name"]) != None:
            image_path = os.path.join(file["path"], file["name"])
            try:
                # Just try if we can successfully open it
                Image.open(image_path)
            except IOError:
                error_counter = _logProblem(
                    error_counter, "Could not open image, is the file corrupted? %s" % image_path)

    return error_counter


def _check_image_type(error_counter, image_type, addon_xml, addon_path):
    images = addon_xml.findall("*//" + image_type)

    icon_fallback = False
    fanart_fallback = False
    if(not images and image_type == "icon"):
        icon_fallback = True
        image = type('image', (object,),
                     {'text': 'icon.png'})()
        images.append(image)
    elif(not images and image_type == "fanart" and ".module." not in addon_path):
        fanart_fallback = True
        image = type('image', (object,),
                     {'text': 'fanart.jpg'})()
        images.append(image)

    for image in images:
        if(image.text):
            filepath = os.path.join(addon_path, image.text)
            if(os.path.isfile(filepath)):
                print("Image %s exists" % image_type)
                try:
                    im = Image.open(filepath)
                    width, height = im.size

                    if image_type == "icon":
                        if((width != 256 and height != 256) and (width != 512 and height != 512)):
                            error_counter = _logProblem(
                                error_counter, "Icon should have either 256x256 or 512x512 but it has %sx%s" % (width, height))
                        else:
                            print("%s dimensions are fine %sx%s" %
                                (image_type, width, height))
                    elif image_type == "fanart":
                        if((width != 1280 and height != 720) and (width != 1920 and height != 1080)):
                            error_counter = _logProblem(
                                error_counter, "Fanart should have either 1280x720 or 1920x1080 but it has %sx%s" % (width, height))
                        else:
                            print("%s dimensions are fine %sx%s" %
                                (image_type, width, height))
                    else:
                        # screenshots have no size definitions
                        pass
                except IOError:
                    error_counter = _logProblem(
                        error_counter, "Could not open image, is the file corrupted? %s" % filepath)

            else:
                # if it's a fallback path addons.xml should still be able to
                # get build
                if fanart_fallback or icon_fallback:
                    error_counter = _logWarning(
                        error_counter, "%s does not exist at specified path." % image_type)
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
        return _logProblem(error_counter, "Not found %s in folder %s" % (file_name, addon_path))
    else:
        return error_counter


def _addon_xml_matches_folder(error_counter, addon_path, addon_xml):
    addon = addon_xml.getroot()
    if os.path.basename(os.path.normpath(addon_path)) == addon.attrib.get("id"):
        print("Addon id matches foldername")
    else:
        error_counter = _logProblem(error_counter, "Addon id and foldername does not match.")
    return error_counter


def _check_for_legacy_strings_xml(error_counter, addon_path):
    if _find_file_recursive("strings.xml", addon_path) is None:
        return error_counter
    else:
        return _logProblem(error_counter, "Found strings.xml in folder %s please migrate to strings.po." % addon_path)


def _find_blacklisted_strings(error_counter, addon_path):
    problem_list = []
    for result in find_in_file(addon_path, problem_list):
        error_counter = _logProblem(error_counter, "Found blacklisted term %s in file %s:%s (%s)" % (
            result["term"], result["searchfile"], result["linenumber"], result["line"]))

    warning_list = []
    for result in find_in_file(addon_path, warning_list):
        error_counter = _logWarning(error_counter, "Found blacklisted term %s in file %s:%s (%s)" % (
            result["term"], result["searchfile"], result["linenumber"], result["line"]))

    return error_counter


def _check_for_legacy_language_path(error_counter, addon_path):
    language_path = os.path.join(addon_path, "resources", "language")
    if os.path.exists(language_path):
        dirs = next(os.walk(language_path))[1]
        found_warning = False
        for dir in dirs:
            if(not found_warning and "resource.language." not in dir):
                error_counter = _logWarning(
                    error_counter, "Using the old language directory structure, please move to the new one.")
                found_warning = True
    return error_counter


def _check_file_whitelist(error_counter, file_index, addon_path):
    if ".module." in addon_path:
        print("Module skipping whitelist")
        return error_counter

    whitelist = r"\.?(py|xml|gif|png|jpg|jpeg|md|txt|po|json|gitignore|markdown|yml|rst|ini|flv|wav|mp4|html|css|lst|pkla|g|template|in|cfg|xsd|directory|help|list|mpeg|pls|info|ttf|xsp|theme|yaml|dict)?$"

    for file in file_index:
        file_parts = file["name"].rsplit(".")
        # Only check file endings if there are file endings... 
        # This will not check "README" or ".gitignore"
        if len(file_parts) > 1:
            file_ending = "." + file_parts[len(file_parts)-1]
            if re.match(whitelist, file_ending.lower()) == None:
                error_counter = _logProblem(error_counter, "Found non whitelisted file ending in filename %s" % (
                    os.path.join(file["path"], file["name"])))

    return error_counter


def _logProblem(error_counter, problem_string):
    colorPrint("PROBLEM: %s" % problem_string, "31")
    error_counter["problems"] = error_counter["problems"] + 1
    return error_counter


def _logWarning(error_counter, warning_string):
    colorPrint("WARNING: %s" % warning_string, "35")
    error_counter["warnings"] = error_counter["warnings"] + 1
    return error_counter
