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
            Record(PROBLEM, "Found %s please migrate to strings.po." % relative_path(file)))


def find_blacklisted_strings(report: Report, addon_path: str, problems: list, warnings: list, file_types: list):
    """Find for any blacklisted strings in the addons files
        :addon_path: Path of theh addon
        :problems: List of all the strings that will cause problem being in an addon
        :warnings: List of all the strings that shouldn't be in addon
                        but doesn't cause any problem
        :file_type: List of the whitelisted files to look into
    """
    for result in handle_files.find_in_file(addon_path, problems, file_types):
        report.add(Record(PROBLEM, "Found blacklisted term %s in file %s:%s (%s)"
                          % (result["term"], result["searchfile"], result["linenumber"], result["line"])))

    for result in handle_files.find_in_file(addon_path, warnings, file_types):
        report.add(Record(WARNING, "Found blacklisted term %s in file %s:%s (%s)"
                          % (result["term"], result["searchfile"], result["linenumber"], result["line"])))


def check_for_invalid_strings_po(report: Report, file_index: list, addon_path: str):
    """Validate strings.po files
        :file_index: list having names and path of all the files present in addon
        :addon_path: Path of the addon
    """
    en_gb_present = False
    report_made = False

    language_path = os.path.join(addon_path, "resources", "language", "resource.language.")

    po_file_index = [f for f in file_index if f["name"] == "strings.po"]

    for po_file in po_file_index:
        success, language_code = parse_po_file(report, language_path, po_file)
        if not en_gb_present and success and language_code and language_code.lower() == 'en_gb':
            en_gb_present = True

        if not report_made and not success:
            report_made = True

    if not en_gb_present:
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
        :language_path: base language path, "<ADDON_PATH>/resources/language/resource.language."
        :po_file: dict containing name and path of the po file representing a file from file_index
    """
    success = True
    full_path = os.path.join(po_file["path"], po_file["name"])

    if not full_path.startswith(language_path):
        success = False
        report.add(Record(PROBLEM, "PO file not in the correct path: %s"
                          % (relative_path(full_path))))
        return success, None

    language_code = po_file["path"].replace(language_path, "")

    if not RE_LANG_CODE.match(language_code):
        success = False
        report.add(Record(PROBLEM, "PO file with invalid language code in the correct path: %s"
                          % (relative_path(full_path))))
        return success, language_code

    with open(full_path, "r", encoding="utf-8") as f:
        try:
            contents = f.read()
            f.seek(0)
            lines = f.readlines()
        except UnicodeDecodeError:
            success = False
            report.add(Record(PROBLEM, "Invalid PO file %s: File is not saved with UTF-8 encoding"
                              % (relative_path(full_path))))
            return success, language_code

    if not contents:
        success = False
        report.add(Record(PROBLEM, "Invalid PO file %s: File is empty" % (relative_path(full_path))))
        return success, language_code

    if "\r\n" in contents:
        success = False
        report.add(Record(WARNING, "Windows line endings found in %s, consider converting to Linux line endings."
                          % relative_path(full_path)))

    header = contents[:contents.find("msgctxt \"#")]
    if not re.search(r'msgid ""\s+msgstr ""', header):
        # This is only required by polib if metadata follows, Kodi requires this regardless of metadata
        success = False
        report.add(Record(PROBLEM, "Invalid PO file %s:\nMissing required header:\n"
                                   "\tmsgid \"\"\n\tmsgstr \"\"" % (relative_path(full_path))))

    if contents[0] == "\ufeff":
        success = False
        report.add(Record(PROBLEM, "Invalid PO file %s: File contains BOM (byte order mark)"
                          % (relative_path(full_path))))
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
                message = "%s on line %s" % (match.group("message"), match.group("line_num"))
                break

        success = False
        report.add(Record(PROBLEM, "Invalid PO file %s: %s" % (relative_path(full_path), message)))

    return success, language_code
