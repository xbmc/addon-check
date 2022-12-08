"""
    Copyright (C) 2021 Team Kodi
    This file is part of Kodi - kodi.tv

    SPDX-License-Identifier: GPL-3.0-only
    See LICENSES/README.md for more information.
"""

import re
from .record import PROBLEM, Record
from .report import Report


def version_is_valid(version):
    """Checks if a version is valid

    Args:
        version (str): The version string

    Returns:
        [bool]: If the version is valid
    """
    return bool(re.match(r"^(\d+\.\d+(\.\d+){0,4}([+~\w]+(\.\d+)?)?)$",
                    version))


def check_version(report: Report, parsed_xml):
    """Checks if the version for the addon defined in addon.xml is valid

    Args:
        report (Report): The report object
        parsed_xml (et.Element): The parsed addon.xml
    """
    if "version" not in parsed_xml.attrib.keys():
        report.add(Record(PROBLEM, "Missing version in addon.xml"))
        return

    if not version_is_valid(parsed_xml.attrib["version"]):
        report.add(Record(PROBLEM, f"Invalid version {parsed_xml.attrib['version']} " \
            "in addon.xml. Please use the major.minor.revision (e.g. 1.0.0) format or " \
            "major.minor.revision+localversion_identifier (e.g. 1.0.0+matrix.1)"))
