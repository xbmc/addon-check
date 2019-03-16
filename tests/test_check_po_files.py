import unittest
from os.path import abspath, dirname, join

from kodi_addon_checker.check_string import check_for_invalid_strings_po
from kodi_addon_checker.common import load_plugins
from kodi_addon_checker.common import relative_path
from kodi_addon_checker.record import Record
from kodi_addon_checker.reporter import ReportManager
from kodi_addon_checker.report import Report

HERE = abspath(dirname(__file__))


class TestPOFiles(unittest.TestCase):
    def setUp(self):
        self.path = join(HERE, "test_data", "PO_files")
        load_plugins()
        ReportManager.enable(["array"])
        self.report = Report("")
        self.report_matches = ("ERROR: Invalid PO file")

    def test_check_for_invalid_strings_po_valid_file(self):
        ReportManager.getEnabledReporters()[0].reports = []

        path = join(self.path, "valid_file")
        file_index = [{"path": path, "name": "strings.po"}]

        expected = []

        check_for_invalid_strings_po(self.report, file_index)

        records = [Record.__str__(r) for r in ReportManager.getEnabledReporters()[0].reports]
        output = [s for s in records if s.startswith(self.report_matches)]

        self.assertListEqual(expected, output)

    def test_check_for_invalid_strings_po_missing_header(self):
        ReportManager.getEnabledReporters()[0].reports = []

        path = join(self.path, "missing_header")
        full_path = join(path, "strings.po")

        file_index = [{"path": path, "name": "strings.po"}]

        expected = ['ERROR: Invalid PO file {path}:\n'
                    'Missing required header:\n'
                    '\tmsgid ""\n\tmsgstr ""'.format(path=relative_path(full_path))]

        check_for_invalid_strings_po(self.report, file_index)

        records = [Record.__str__(r) for r in ReportManager.getEnabledReporters()[0].reports]
        output = [s for s in records if s.startswith(self.report_matches)]

        self.assertListEqual(expected, output)

    def test_check_for_invalid_strings_po_syntax_error(self):
        ReportManager.getEnabledReporters()[0].reports = []

        path = join(self.path, "syntax_error")
        full_path = join(path, "strings.po")

        file_index = [{"path": path, "name": "strings.po"}]

        expected = ["ERROR: Invalid PO file {path}: "
                    "Syntax error on line 19".format(path=relative_path(full_path))]

        check_for_invalid_strings_po(self.report, file_index)

        records = [Record.__str__(r) for r in ReportManager.getEnabledReporters()[0].reports]
        output = [s for s in records if s.startswith(self.report_matches)]

        self.assertListEqual(expected, output)

    def test_check_for_invalid_strings_po_encoding(self):
        ReportManager.getEnabledReporters()[0].reports = []

        path = join(self.path, "encoding")
        full_path = join(path, "strings.po")

        file_index = [{"path": path, "name": "strings.po"}]

        expected = ["ERROR: Invalid PO file {path}: "
                    "File is not saved with UTF-8 encoding".format(path=relative_path(full_path))]

        check_for_invalid_strings_po(self.report, file_index)

        records = [Record.__str__(r) for r in ReportManager.getEnabledReporters()[0].reports]
        output = [s for s in records if s.startswith(self.report_matches)]

        self.assertListEqual(expected, output)

    def test_check_for_invalid_strings_po_bom(self):
        ReportManager.getEnabledReporters()[0].reports = []

        path = join(self.path, "bom")
        full_path = join(path, "strings.po")

        file_index = [{"path": path, "name": "strings.po"}]

        expected = ["ERROR: Invalid PO file {path}: "
                    "File contains BOM (byte order mark)".format(path=relative_path(full_path))]

        check_for_invalid_strings_po(self.report, file_index)

        records = [Record.__str__(r) for r in ReportManager.getEnabledReporters()[0].reports]
        output = [s for s in records if s.startswith(self.report_matches)]

        self.assertListEqual(expected, output)

    def test_check_for_invalid_strings_po_empty(self):
        ReportManager.getEnabledReporters()[0].reports = []

        path = join(self.path, "empty")
        full_path = join(path, "strings.po")

        file_index = [{"path": path, "name": "strings.po"}]

        expected = ["ERROR: Invalid PO file {path}: File is empty".format(path=relative_path(full_path))]

        check_for_invalid_strings_po(self.report, file_index)

        records = [Record.__str__(r) for r in ReportManager.getEnabledReporters()[0].reports]
        output = [s for s in records if s.startswith(self.report_matches)]

        self.assertListEqual(expected, output)
