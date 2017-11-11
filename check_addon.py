from PIL import Image
from common import colorPrint
import os
import sys
import re
import xml.etree.ElementTree


def find_file(name, path):
    for file in os.listdir(path):
        match = re.match(name, file)
        if match != None:
            return os.path.join(path, match.string)
    return


# this looks for a file but only returns the first occurance
def find_file_recursive(name, path):
    for file in os.walk(path):
        if name in file[2]:
            print("Found " + name)
            return os.path.join(path, name)
    return


def find_in_file(path, search_terms):
    results = []
    if len(search_terms) > 0:
        for dir in os.walk(path):
            for file in dir[2]:
                file_path = os.path.join(dir[0], file)
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


def find_file_name(path, search_terms):
    results = []

    if len(search_terms) > 0:
        for dir in os.walk(path):
            for file in dir[2]:
                for term in search_terms:
                    if term in file:
                        file_path = os.path.join(dir[0], file)
                        results.append({"term": term, "searchfile": file_path})
    return results


def check_config(config, value):
    return config is None or config[value] is True

def check_addon(error_counter, addon_path, config = None):
    colorPrint("Checking %s" % os.path.basename(
        os.path.normpath(addon_path)), "34")

    error_counter, addon_xml = check_addon_xml(error_counter, addon_path)

    if addon_xml != None:
        if len(addon_xml.findall("*//broken")) == 0:
            error_counter = check_artwork(error_counter, addon_path, addon_xml)

            if check_config(config, "check_license_file_exists"):
                # check if license file is existing
                error_counter = addon_file_exists(error_counter, addon_path, "LICENSE\.txt|LICENSE\.md|LICENSE")

            if check_config(config, "check_legacy_strings_xml"):
                error_counter = check_for_legacy_strings_xml(error_counter, addon_path)

            if check_config(config, "check_legacy_language_path"):
                error_counter = check_for_legacy_language_path(error_counter, addon_path)

            error_counter = find_blacklisted_strings(error_counter, addon_path)

            error_counter = find_blacklisted_files(error_counter, addon_path)
        else:
            print "Addon marked as broken - skipping"

    return error_counter


def check_addon_xml(error_counter, addon_path):
    addon_xml_path = os.path.join(addon_path, "addon.xml")
    addon_xml = None
    try:
        error_counter = addon_file_exists(error_counter, addon_path, "addon\.xml")

        addon_xml = xml.etree.ElementTree.parse(addon_xml_path)
        addon = addon_xml.getroot()
        colorPrint ("created by %s" % addon.attrib.get("provider-name"), "34")
        error_counter = addon_xml_matches_folder(error_counter, addon_path, addon_xml)
    except xml.etree.ElementTree.ParseError:
        error_counter = logProblem(error_counter, "Addon xml not valid, check xml. %s" % addon_xml_path)
    return error_counter, addon_xml


def check_artwork(error_counter, addon_path, addon_xml):
    # icon, fanart, screenshot
    error_counter = check_image_type(error_counter, "icon", addon_xml, addon_path)
    error_counter = check_image_type(error_counter, "fanart", addon_xml, addon_path)
    error_counter = check_image_type(error_counter, "screenshot", addon_xml, addon_path)

    return error_counter


def check_image_type(error_counter, image_type, addon_xml, addon_path):
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
                            error_counter = logProblem(
                                error_counter, "Icon should have either 256x256 or 512x512 but it has %sx%s" % (width, height))
                        else:
                            print("%s dimensions are fine %sx%s" %
                                (image_type, width, height))
                    elif image_type == "fanart":
                        if((width != 1280 and height != 720) and (width != 1920 and height != 1080)):
                            error_counter = logProblem(
                                error_counter, "Fanart should have either 1280x720 or 1920x1080 but it has %sx%s" % (width, height))
                        else:
                            print("%s dimensions are fine %sx%s" %
                                (image_type, width, height))
                    else:
                        # screenshots have no size definitions
                        pass
                except IOError:
                    error_counter = logProblem(
                        error_counter, "Could not open image, is the file corrupted? %s" % filepath)

            else:
                # if it's a fallback path addons.xml should still be able to
                # get build
                if fanart_fallback or icon_fallback:
                    error_counter = logWarning(
                        error_counter, "%s does not exist at specified path." % image_type)
                # it's no fallback path, so building addons.xml will crash -
                # this is a problem ;)
                else:
                    error_counter = logProblem(
                        error_counter, "%s does not exist at specified path." % image_type)
        else:
            error_counter = logWarning(
                error_counter, "Empty image tag found for %s" % image_type)
    return error_counter


def addon_file_exists(error_counter, addon_path, file_name):
    if find_file(file_name, addon_path) is None:
        return logProblem(error_counter, "Not found %s in folder %s" % (file_name, addon_path))
    else:
        return error_counter


def addon_xml_matches_folder(error_counter, addon_path, addon_xml):
    addon = addon_xml.getroot()
    if os.path.basename(os.path.normpath(addon_path)) == addon.attrib.get("id"):
        print("Addon id matches foldername")
    else:
        error_counter = logProblem(error_counter, "Addon id and foldername does not match.")
    return error_counter


def check_for_legacy_strings_xml(error_counter, addon_path):
    if find_file_recursive("strings.xml", addon_path) is None:
        return error_counter
    else:
        return logProblem(error_counter, "Found strings.xml in folder %s please migrate to strings.po." % addon_path)


def find_blacklisted_strings(error_counter, addon_path):
    problem_list = []
    for result in find_in_file(addon_path, problem_list):
        error_counter = logProblem(error_counter, "Found blacklisted term %s in file %s:%s (%s)" % (
            result["term"], result["searchfile"], result["linenumber"], result["line"]))

    warning_list = []
    for result in find_in_file(addon_path, warning_list):
        error_counter = logWarning(error_counter, "Found blacklisted term %s in file %s:%s (%s)" % (
            result["term"], result["searchfile"], result["linenumber"], result["line"]))

    return error_counter


def check_for_legacy_language_path(error_counter, addon_path):
    language_path = os.path.join(addon_path, "resources", "language")
    if os.path.exists(language_path):
        dirs = next(os.walk(language_path))[1]
        found_warning = False
        for dir in dirs:
            if(not found_warning and "resource.language." not in dir):
                error_counter = logWarning(
                    error_counter, "Using the old language directory structure, please move to the new one.")
                found_warning = True
    return error_counter


def find_blacklisted_files(error_counter, addon_path):
    problem_list = [".so", ".dll", ".pyo", ".exe",
                    ".xbt", ".xpr", "Thumbs.db", ".pdf", ".doc"]
    for result in find_file_name(addon_path, problem_list):
        error_counter = logProblem(error_counter, "Found blacklisted term %s in filename %s" % (
            result["term"], result["searchfile"]))

    warning_list = []
    for result in find_file_name(addon_path, warning_list):
        error_counter = logWarning(error_counter, "Found blacklisted term %s in filename %s" % (
            result["term"], result["searchfile"]))

    return error_counter


def logProblem(error_counter, problem_string):
    colorPrint("PROBLEM: %s" % problem_string, "31")
    error_counter["problems"] = error_counter["problems"] + 1
    return error_counter


def logWarning(error_counter, warning_string):
    colorPrint("WARNING: %s" % warning_string, "35")
    error_counter["warnings"] = error_counter["warnings"] + 1
    return error_counter
