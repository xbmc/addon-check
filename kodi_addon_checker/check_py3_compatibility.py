"""
    Copyright (C) 2017-2018 Team Kodi
    This file is part of Kodi - kodi.tv

    SPDX-License-Identifier: GPL-3.0-only
    See LICENSES/README.md for more information.
"""

import os

from lib2to3 import pgen2
from lib2to3 import refactor
import difflib

from .common import relative_path
from .report import Report
from .record import Record, INFORMATION, PROBLEM


class KodiRefactoringTool(refactor.RefactoringTool):

    def __init__(self, report, log_level, *args, **kwargs):
        self.report = report
        self.log_level = log_level
        super(KodiRefactoringTool, self).__init__(*args, **kwargs)

    def print_output(self, old, new, filepath, equal):
        """
        Called with the old version, new version, and filepath of a
        refactored file.

            :old: old text of refactored file
            :new: new text of refactored file
            :filepath: Path of the file
            :equal: Tells whether or not old is equal to new
        """

        if equal:
            return

        diff = ""
        for line in difflib.unified_diff(old.splitlines(), new.splitlines(),
                                         relative_path(filepath), relative_path(filepath),
                                         "(original)", "(refactored)", n=3, lineterm=""):
            diff += line + "\n"

        self.report.add(Record(self.log_level, relative_path(filepath) + '\n' + diff[:-1]))


def check_py3_compatibility(report: Report, path: str, branch_name: str):
    """
     Checks compatibility of addons with python3
        :path: path to the addon
    """
    list_of_fixes = [
                     'except',
                     'exec',
                     'ne',
                     'raise',
                     'repr',
                     'tuple_params',
                    ]

    fixer_names = ['lib2to3.fixes.fix_' + fix for fix in list_of_fixes]

    rt = KodiRefactoringTool(report, PROBLEM, fixer_names, options=None, explicit=None)
    try:
        rt.refactor([path])
    except pgen2.parse.ParseError as e:
        report.add(Record(PROBLEM, "ParseError: {}".format(e)))

    if branch_name not in ['gotham', 'helix', 'isengard', 'jarvis']:
        list_of_fixes = [
                        'dict',
                        'filter',
                        'has_key',
                        'import',
                        'itertools',
                        'map',
                        'next',
                        'numliterals',
                        'print',
                        'renames',
                        'types',
                        'xrange',
                        'zip',
                        ]

        fixer_names = ['lib2to3.fixes.fix_' + fix for fix in list_of_fixes]

        rt = KodiRefactoringTool(report, INFORMATION, fixer_names, options=None, explicit=None)
        try:
            rt.refactor([path])
        except pgen2.parse.ParseError as e:
            report.add(Record(INFORMATION, "ParseError: {}".format(e)))
