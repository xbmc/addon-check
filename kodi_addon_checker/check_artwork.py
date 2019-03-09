"""
    Copyright (C) 2017-2018 Team Kodi
    This file is part of Kodi - kodi.tv

    SPDX-License-Identifier: GPL-3.0-only
    See LICENSES/README.md for more information.
"""

import logging
import os
import re

from PIL import Image

from .common import has_transparency, relative_path
from .record import INFORMATION, PROBLEM, WARNING, Record
from .report import Report

LOGGER = logging.getLogger(__name__)


def check_artwork(report: Report, addon_path: str, parsed_xml, file_index: list, branch_name: str):
    """Checks for icon/fanart/screenshot
        :addon_path: path to the folder having addon files
        :parsed_xml: xml file i.e addon.xml
        :file_index: list having name and path of all the files in an addon
    """
    art_type = ['icon', 'fanart', 'screenshot']
    for image_type in art_type:
        _check_image_type(report, image_type, parsed_xml, addon_path, branch_name)

    for file in file_index:
        if re.match(r"(?!fanart\.jpg|icon\.png).*\.(png|jpg|jpeg|gif)$", file["name"]) is not None:
            image_path = os.path.join(file["path"], file["name"])
            try:
                Image.open(image_path)
            except IOError:
                report.add(
                    Record(PROBLEM, "Could not open image, is the file corrupted ? %s" % relative_path(image_path)))


def _check_image_type(report: Report, image_type: str, parsed_xml, addon_path: str, branch_name: str):
    """Check for whether the given image type exists or not if they do """

    fallback, images = _assests(image_type, parsed_xml, addon_path)

    for image in images:
        if image:
            filepath = os.path.join(addon_path, image)

            if os.path.isfile(filepath):
                report.add(Record(INFORMATION, "Image %s exists" % image_type))
                if fallback and branch_name not in ['gotham', 'helix', 'isengard', 'jarvis']:
                    report.add(Record(
                        PROBLEM, "Image %s should be explicitly declared in addon.xml <assets>." % image_type))
                try:
                    im = Image.open(filepath)
                    width, height = im.size

                    if image_type == "icon":
                        _check_icon(report, im, width, height)

                    elif image_type == "fanart":
                        _check_fanart(report, width, height)
                    else:
                        # screenshots have no size definitions
                        if has_transparency(im):
                            report.add(Record(PROBLEM, "%s should be solid. It has transparency." % image))
                        LOGGER.info("Artwork was a screenshot")
                except IOError:
                    report.add(
                        Record(PROBLEM, "Could not open image, is the file corrupted? %s" % relative_path(filepath)))

            else:
                # if it's a fallback path addons.xml should still be able to
                # get build
                if fallback:
                    report.add(Record(INFORMATION, "You might want to add a %s" % image_type))
                # it's no fallback path, so building addons.xml will crash -
                # this is a problem ;)
                else:
                    report.add(
                        Record(PROBLEM, "%s does not exist at specified path." % image_type))
        else:
            report.add(
                Record(WARNING, "Empty image tag found for %s" % image_type))


def _assests(image_type: str, parsed_xml, addon_path: str):
    """"""
    images = [image.text for image in parsed_xml.findall("./extension/assets/" + image_type)]

    fallback = False

    if not images and image_type == "icon":
        fallback = True
        images.append('icon.png')
    elif not images and image_type == "fanart":
        skip_addon_types = [".module.", "metadata.", "context.", ".language."]
        for addon_type in skip_addon_types:
            if addon_type in addon_path:
                break
        else:
            fallback = True
            images.append('fanart.jpg')

    return fallback, images


def _check_icon(report: Report, im, width, height):
    """Check the icon of the addon for transparency and dimensions

        :im: PIL.Image object
        :width: width of the icon
        :height: height of the icon
    """
    if has_transparency(im):
        report.add(Record(PROBLEM, "Icon.png should be solid. It has transparency."))

    icon_sizes = [(256, 256), (512, 512)]

    if (width, height) not in icon_sizes:
        report.add(Record(PROBLEM, "Icon should have either 256x256 or 512x512 but it has %sx%s" % (
            width, height)))
    else:
        report.add(
            Record(INFORMATION, "Icon dimensions are fine %sx%s" % (width, height)))


def _check_fanart(report: Report, width, height):
    """Check the dimensions of the fanart

        :width: width of the icon
        :height: height of the icon
    """
    fanart_sizes = [(1280, 720), (1920, 1080), (3840, 2160)]
    fanart_sizes_str = " or ".join(["%dx%d" % (w, h) for w, h in fanart_sizes])

    if (width, height) not in fanart_sizes:
        report.add(Record(PROBLEM, "Fanart should have either %s but it has %sx%s" % (
            fanart_sizes_str, width, height)))
    else:
        report.add(Record(INFORMATION, "Fanart dimensions are fine %sx%s" % (width, height)))
