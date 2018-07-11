import os

from lib2to3 import refactor
from tabulate import tabulate

from .report import Report
from .record import Record, INFORMATION


class KodiRefactoringTool(refactor.RefactoringTool):

    def __init__(self, report, *args, **kwargs):
        self.report = report
        super(KodiRefactoringTool, self).__init__(*args, **kwargs)

    def short_path(self, path):
        return os.path.split(path)[1]

    def print_output(self, old, new, filepath, equal):
        """
        Called with the old version, new version, and filepath of a
        refactored file.

            :old: old text of refactored file
            :new: new text of refactored file
            :filepath: Path of the file
            :equal: Tells whether or not old is equal to new
        """

        self.headers = ['#', 'Existing Code', 'Changes required']
        self.table = []

        if equal:
            return

        required_changes = new.splitlines()
        existing_line = old.splitlines()

        for line in range(min(len(required_changes), len(existing_line))):
            if existing_line[line] != required_changes[line]:
                self.table.append([line + 1, existing_line[line], required_changes[line]])

        self.output = tabulate(self.table, headers=self.headers, tablefmt='fancy_grid')
        self.report.add(Record(INFORMATION, self.short_path(filepath) + '\n' + self.output))


def Check_Py3_compatibility(report: Report, path: str):
    """
     Checks compatibility of addons with python3
        :path: path to the addon
    """
    fixer_names = []
    list_of_fixes = ['import', 'dict', 'except', 'filter', 'has_key', 'itertools',
                     'map', 'ne', 'next', 'print', 'renames', 'types', 'xrange', 'zip']

    for fix in list_of_fixes:
        fixer_names.append('lib2to3.fixes.fix_' + fix)

    rt = KodiRefactoringTool(report, fixer_names, options=None, explicit=None)
    rt.refactor([path])
