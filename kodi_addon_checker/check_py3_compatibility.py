"""
    Copyright (C) 2017-2018 Team Kodi
    This file is part of Kodi - kodi.tv

    SPDX-License-Identifier: GPL-3.0-only
    See LICENSES/README.md for more information.
"""

import difflib
from lib2to3 import pgen2, refactor # pylint: disable=deprecated-module

from .common import relative_path
from .record import INFORMATION, PROBLEM, Record
from .report import Report
from .versions import KodiVersion


class KodiRefactoringTool(refactor.RefactoringTool):

    def __init__(self, report, log_level, *args, **kwargs):
        self.report = report
        self.log_level = log_level
        super().__init__(*args, **kwargs)

    def print_output(self, old_text, new_text, filename, equal):
        """
        Called with the old version, new version, and filepath of a
        refactored file.

            :old_text: old text of refactored file
            :new_text: new text of refactored file
            :filename: Path of the file
            :equal: Tells whether or not old is equal to new
        """

        if equal:
            return

        diff = ""
        for line in difflib.unified_diff(old_text.splitlines(), new_text.splitlines(),
                                         relative_path(filename), relative_path(filename),
                                         "(original)", "(refactored)", n=3, lineterm=""):
            diff += line + "\n"

        self.report.add(Record(self.log_level, relative_path(filename) + '\n' + diff[:-1]))


def check_py3_compatibility(report: Report, path: str, kodi_version: KodiVersion):
    """
     Checks compatibility of addons with python3
        :path: path to the addon
    """
    list_of_fixes = [
        'except',
        'exec',
        'ne',
        'print',
        'raise',
        'repr',
        'tuple_params',
    ]

    fixer_names = ['lib2to3.fixes.fix_' + fix for fix in list_of_fixes]

    rt = KodiRefactoringTool(report, PROBLEM, fixer_names, options={"print_function": True}, explicit=None)
    try:
        rt.refactor([path])
    except pgen2.parse.ParseError:
        rt = KodiRefactoringTool(report, PROBLEM, fixer_names, options=None, explicit=None)
        try:
            rt.refactor([path])
        except pgen2.parse.ParseError as pe:
            report.add(Record(PROBLEM, f"ParseError: {pe}"))
        except UnicodeDecodeError as ude:
            report.add(Record(PROBLEM, f"UnicodeDecodeError: {ude}"))
    except UnicodeDecodeError as ude:
        report.add(Record(PROBLEM, f"UnicodeDecodeError: {ude}"))

    if kodi_version >= KodiVersion("krypton"):
        list_of_fixes = [
                        'dict',
                        'filter',
                        'has_key',
                        'import',
                        'itertools',
                        'map',
                        'next',
                        'numliterals',
                        'renames',
                        'types',
                        'xrange',
                        'zip',
                        ]

        fixer_names = ['lib2to3.fixes.fix_' + fix for fix in list_of_fixes]

        rt = KodiRefactoringTool(report, INFORMATION, fixer_names, options={"print_function": True}, explicit=None)
        try:
            rt.refactor([path])
        except pgen2.parse.ParseError:
            rt = KodiRefactoringTool(report, INFORMATION, fixer_names, options=None, explicit=None)
            try:
                rt.refactor([path])
            except pgen2.parse.ParseError as pe:
                report.add(Record(INFORMATION, f"ParseError: {pe}"))
            except UnicodeDecodeError as ude:
                report.add(Record(PROBLEM, f"UnicodeDecodeError: {ude}"))
        except UnicodeDecodeError as ude:
            report.add(Record(PROBLEM, f"UnicodeDecodeError: {ude}"))
