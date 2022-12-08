"""
    Copyright (C) 2017-2018 Team Kodi
    This file is part of Kodi - kodi.tv

    SPDX-License-Identifier: GPL-3.0-only
    See LICENSES/README.md for more information.
"""

import os

from radon.raw import analyze

from .record import PROBLEM, WARNING, Record
from .report import Report


def check_complex_addon_entrypoint(report: Report, addon_path: str, parsed_xml, max_entrypoint_count: int):
    """check the complexity of the addon.xml file by counting the number of lines in the file.
        :addon_path: path of the addon
        :parsed_xml: parsed addon.xml file
        :max_entrypoint_count: :max_entypoint_line_count: max value allowed in any entrypoint file
    """

    for i in parsed_xml.findall("extension"):
        library = i.get("library")

        if library:
            filepath = os.path.join(addon_path, library)

            if not os.path.isdir(filepath):
                ext = os.path.splitext(filepath)

                if os.path.exists(filepath):
                    if ext[1] == '.py':
                        _number_of_lines(report, filepath, library,
                                         max_entrypoint_count)
                else:
                    report.add(
                        Record(PROBLEM, f"{library} Entry point does not exists"))


def _number_of_lines(report: Report, filepath: str, library: str, max_entrypoint_count: int):
    """Returns the number of logical lines of code in a given python file
        :filepath: Path of the python file
        :library: relative path of the file
        :max_entypoint_line_count: max value allowed in any entrypoint file
    """

    try:
        with open(filepath, 'r', encoding="utf-8") as file:
            data = file.read()

        lineno = analyze(data).lloc
        if lineno >= max_entrypoint_count:
            report.add(Record(WARNING,
                              f"Complex entry point. Check: {library} | "
                              f"Counted lines: {lineno} | Lines allowed: {max_entrypoint_count}"))

    except UnicodeDecodeError as e:
        report.add(Record(PROBLEM, f"UnicodeDecodeError: {e}"))

    except SyntaxError as e:
        if e.msg == 'SyntaxError at line: 1':
            report.add(Record(PROBLEM,
                              (f"Error parsing file, is your file saved with UTF-8 encoding? "
                               f"Make sure it has no BOM. Check: {library}")))
        else:
            report.add(Record(PROBLEM,
                               "Error parsing file, is there a syntax error in your file?" \
                               f"Check: {library}"))
