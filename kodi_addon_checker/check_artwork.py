"""
    Copyright (C) 2017-2018 Team Kodi
    This file is part of Kodi - kodi.tv

    SPDX-License-Identifier: GPL-3.0-only
    See LICENSES/README.md for more information.
"""

import logging
import os
import re

from collections import namedtuple
from PIL import Image

from .common import has_transparency, relative_path
from .record import INFORMATION, PROBLEM, WARNING, Record
from .report import Report
from .versions import KodiVersion


LOGGER = logging.getLogger(__name__)


def check_artwork(report: Report, addon_path: str, parsed_xml, file_index: list, kodi_version: KodiVersion):
    """Checks for icon/fanart/screenshot
        :addon_path: path to the folder having addon files
        :parsed_xml: xml file i.e addon.xml
        :file_index: list having name and path of all the files in an addon
    """
    Asset = namedtuple('Asset', ['image_type', 'specifications'])

    art_assets = [
        Asset(
            'icon',
            {
                'extension': ['.png'],
                'transparency': False,
                'sizes': [(256, 256), (512, 512)],
                'max_file_size': None
            }
        ),
        Asset(
            'fanart',
            {
                'extension':
                    # fanart no longer hardcoded/assets element added as of Krypton, allow .png
                    [".jpg", ".jpeg", ".png"]
                    if kodi_version >= KodiVersion("krypton") else
                    [".jpg", ".jpeg"],
                'transparency': None,
                'sizes': [(1280, 720), (1920, 1080), (3840, 2160)],
                'max_file_size': 1000
            }
        ),
        Asset(
            'screenshot',
            {
                'extension': [".jpg", ".jpeg", ".png"],
                'transparency': False,
                'sizes': [(1280, 720), (1920, 1080)],
                'max_file_size': 750
            }
        ),
        Asset(
            'banner',
            {
                'extension': [".jpg", ".jpeg", ".png"],
                'transparency': False,
                'sizes': [(1000, 185)],
                'max_file_size': None
            }
        ),
        Asset(
            'clearlogo',
            {
                'extension': ['.png'],
                'transparency': True,
                'sizes': [(400, 155), (800, 310)],
                'max_file_size': None
            }
        )
    ]

    for asset in art_assets:
        _check_image_type(report, asset, parsed_xml, addon_path, kodi_version)

    for file in file_index:
        if re.match(r"(?!fanart\.jpg|icon\.png).*\.(png|jpg|jpeg|gif)$", file["name"]) is not None:
            image_path = os.path.join(file["path"], file["name"])
            try:
                Image.open(image_path)
            except IOError:
                report.add(
                    Record(PROBLEM, f"Could not open image, is the file corrupted ? {relative_path(image_path)}"))


def _check_image_type(report: Report, asset: tuple, parsed_xml, addon_path: str, kodi_version: KodiVersion):
    """Check for whether the given image type exists or not if they do """

    fallback, images = _assets(asset.image_type, parsed_xml, addon_path)

    for image in images:
        if image:
            filepath = os.path.join(addon_path, image)

            if os.path.isfile(filepath):
                report.add(Record(INFORMATION, f"Image {asset.image_type} exists"))
                if fallback and kodi_version >= KodiVersion("krypton"):
                    report.add(Record(
                        PROBLEM, f"Image {asset.image_type} should be explicitly declared in addon.xml <assets>."))
                try:
                    im = Image.open(filepath)
                    # check image specifications
                    _check_art_asset_specifications(report, filepath, im, asset)
                    # close handler
                    im.close()
                except IOError:
                    report.add(
                        Record(PROBLEM, f"Could not open image, is the file corrupted? {relative_path(filepath)}"))

            else:
                # if it's a fallback path addons.xml should still be able to
                # get build
                if fallback:
                    report.add(Record(INFORMATION, f"You might want to add a {asset.image_type}"))
                # it's no fallback path, so building addons.xml will crash -
                # this is a problem ;)
                else:
                    report.add(
                        Record(PROBLEM, f"{asset.image_type} does not exist at specified path."))
        else:
            report.add(
                Record(WARNING, f"Empty image tag found for {asset.image_type}"))


def _assets(image_type: str, parsed_xml, addon_path: str):
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


def _check_art_asset_specifications(report: Report, filepath, im, asset):
    """Check the art asset specifications (dimensions, transparency, extension)

        :filepath: file path of the image
        :im: PIL.Image object
        :asset: Asset namedtuple
    """
    _, fileextension = os.path.splitext(filepath)
    width, height = im.size
    max_file_size_kb = asset.specifications.get('max_file_size')

    # extension check
    if fileextension not in asset.specifications['extension']:
        report.add(Record(PROBLEM, f"Allowed format for {asset.image_type} is"
         f"{str(asset.specifications['extension'])}, provided {asset.image_type} is {fileextension}."))

    # transparency check
    if asset.specifications['transparency'] is not None:
        if has_transparency(im) and not asset.specifications['transparency']:
            report.add(Record(PROBLEM, f"{asset.image_type} should be solid. It has transparency."))
        elif not has_transparency(im) and asset.specifications['transparency']:
            report.add(Record(PROBLEM, f"{asset.image_type} should have transparency. It is solid."))

    # dimensions check
    if (width, height) not in asset.specifications['sizes']:
        if len(asset.specifications['sizes']) > 1:
            log_str = "either " + \
                " or ".join([f"{w}x{h}" for w, h in asset.specifications['sizes']])
        else:
            log_str = f"{asset.specifications['sizes'][0][0]}x{asset.specifications['sizes'][0][1]}"
        report.add(Record(PROBLEM, f"{asset.image_type} should have {log_str} but it has {width}x{height}"))
    else:
        report.add(Record(INFORMATION, f"{asset.image_type} dimensions are fine {width}x{height}"))

    if isinstance(max_file_size_kb, int):
        file_size_b = os.stat(filepath).st_size
        file_size_kb = str(file_size_b // 1024)
        max_file_size_b = max_file_size_kb * 1024

        if file_size_b <= max_file_size_b:
            report.add(Record(INFORMATION, f"{asset.image_type} file size is fine {file_size_kb}KB"))
        else:
            if asset.image_type == "fanart" and fileextension == ".png":
                report.add(Record(PROBLEM, f"{asset.image_type} is too large {file_size_kb}KB, "
                                           f"maximum file size of {str(max_file_size_kb)}KB. "
                                           f"Consider converting to JPEG"))

            else:
                report.add(Record(PROBLEM, f"{asset.image_type} is too large {file_size_kb}KB, "
                                           f"maximum file size of {str(max_file_size_kb)}KB."))
