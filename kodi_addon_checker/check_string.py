"""
    Copyright (C) 2017-2018 Team Kodi
    This file is part of Kodi - kodi.tv

    SPDX-License-Identifier: GPL-3.0-only
    See LICENSES/README.md for more information.
"""

import os
import re

import polib

from . import handle_files
from .common import relative_path
from .record import INFORMATION, PROBLEM, WARNING, Record
from .report import Report

RE_LANG_CODE = re.compile(r"^[a-z]{2,3}(?:_[a-zA-Z]{2}(?:@\S+)?)?$")


def check_for_legacy_strings_xml(report: Report, addon_path: str):
    """Find for the string.xml file in addon which was used in old versions
        :addon_path: path of the addon
    """
    for file in handle_files.find_files_recursive("strings.xml", os.path.join(addon_path, "resources", "language")):
        report.add(
            Record(PROBLEM, f"Found {relative_path(file)} please migrate to strings.po."))


def find_blacklisted_strings(report: Report, addon_path: str, problems: list, warnings: list, file_types: list):
    """Find for any blacklisted strings in the addons files
        :addon_path: Path of theh addon
        :problems: List of all the strings that will cause problem being in an addon
        :warnings: List of all the strings that shouldn't be in addon
                        but doesn't cause any problem
        :file_type: List of the whitelisted files to look into
    """
    for result in handle_files.find_in_file(addon_path, problems, file_types):
        report.add(Record(PROBLEM, f"Found blacklisted term {result['term']} in file "\
                     f"{result['searchfile']}:{result['linenumber']} ({result['line']})"))

    for result in handle_files.find_in_file(addon_path, warnings, file_types):
        report.add(Record(WARNING, f"Found blacklisted term {result['term']} in file "\
                    f"{result['searchfile']}:{result['linenumber']} ({result['line']})"))


def check_for_invalid_strings_po(report: Report, file_index: list, is_language_addon: bool = False):
    """Validate strings.po files
        :file_index: list having names and path of all the files present in addon
    """
    en_gb_present = False
    report_made = False

    po_file_index = [f for f in file_index if f["name"] == "strings.po"]

    for po_file in po_file_index:
        success, language_code = parse_po_file(report, po_file.get("path"), po_file)
        if not en_gb_present and success and language_code and language_code.lower() == 'en_gb':
            en_gb_present = True

        if not report_made and not success:
            report_made = True

    skip_en_gb_validation = is_language_addon or all(
        (
            _is_using_legacy_language_directory_structure(po_file.get("path")) \
            for po_file in po_file_index
        )
    )

    if not en_gb_present and not skip_en_gb_validation:
        if po_file_index:
            report_made = True
            report.add(Record(PROBLEM, "Required default language 'en_gb' is not present."))
        else:
            report.add(Record(WARNING, "No PO files found. "
                                       "Consider adding language support to your add-on."))

    if po_file_index and not report_made:
        report.add(Record(INFORMATION, "PO files are valid"))


def parse_po_file(report: Report, language_path: str, po_file: dict):
    """Parse strings.po files
        :language_path: base language path, "<ADDON_PATH>/resources/language/resource.language.
        or <ADDON_PATH>/resources/language/language (legacy)"
        :po_file: dict containing name and path of the po file representing a file from file_index
    """
    success = True
    full_path = os.path.join(po_file["path"], po_file["name"])

    language_code = ''
    if len(language_path.rpartition('.')) == 3:
        language_code = language_path.rpartition('.')[2]

    if not _is_using_legacy_language_directory_structure(po_file["path"]) \
        and not RE_LANG_CODE.match(language_code):
        success = False
        report.add(Record(PROBLEM, "PO file with invalid language code in the correct path: " \
            f"{relative_path(full_path)}"))
        return success, language_code

    with open(full_path, "r", encoding="utf-8") as f:
        try:
            contents = f.read()
            f.seek(0)
            lines = f.readlines()
        except UnicodeDecodeError:
            success = False
            report.add(Record(PROBLEM,
                f"Invalid PO file {relative_path(full_path)}: File is not saved with UTF-8 encoding"))
            return success, language_code

    if not contents:
        success = False
        report.add(Record(PROBLEM,
            f"Invalid PO file {relative_path(full_path)}: File is empty"))
        return success, language_code

    if "\r\n" in contents:
        success = False
        report.add(Record(WARNING,
            f"Windows line endings found in {relative_path(full_path)}, consider converting to Linux line endings."
        ))

    header = contents[:contents.find("msgctxt \"#")]
    if not re.search(r'msgid ""\s+msgstr ""', header):
        # This is only required by polib if metadata follows, Kodi requires this regardless of metadata
        success = False
        report.add(Record(PROBLEM, f"Invalid PO file {relative_path(full_path)}:\nMissing required header:\n"
                                   "\tmsgid \"\"\n\tmsgstr \"\""))

    if contents[0] == "\ufeff":
        success = False
        report.add(Record(PROBLEM, f"Invalid PO file {relative_path(full_path)}: File contains BOM (byte order mark)"))
        return success, language_code

    # fix any Gettext automatic comments in the source before testing with polib
    contents = ''.join(['# ' + line.replace('#', '').lstrip()
                        if (line.startswith('#') and line.replace('#', '').lstrip())
                        else ('\n'
                              if line.startswith('#') and not line.replace('#', '').lstrip()
                              else line)
                        for line in lines])
    try:
        polib.pofile(contents, encoding="utf-8")
    except OSError as error:
        # raised on the first syntax error
        message = str(error)
        patterns = [r"\(line (?P<line_num>[0-9]+)\)\s*:\s*(?P<message>[\s\S]+)\s*$",
                    r"(?P<message>Syntax error)[\s\S]+\(line (?P<line_num>[0-9]+)\)\s*$"]
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                # restructure message to remove file and path
                message = f"{match.group('message')} on line {match.group('line_num')}"
                break

        success = False
        report.add(Record(PROBLEM, f"Invalid PO file {relative_path(full_path)}: {message}"))

    return success, language_code


def _is_using_legacy_language_directory_structure(po_file: str):
    """Checks if all the po files in the addon directory are not
    using the new language folder layout

    Args:
        po_file (str): Path to the po file

    Returns:
        [bool]: If addon is using legacy directory path
    """

    return "resource.language." not in po_file
