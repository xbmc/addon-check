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
        self.report_matches = "ERROR: Invalid PO file"

    def test_check_for_invalid_strings_po_valid_file(self):
        ReportManager.getEnabledReporters()[0].reports = []

        path = join(self.path, "valid_file")
        language_path = join(path, "resources", "language", "resource.language.en_gb")

        file_index = [{"path": language_path, "name": "strings.po"}]

        expected = []
        check_for_invalid_strings_po(self.report, file_index)

        records = [Record.__str__(r) for r in ReportManager.getEnabledReporters()[0].reports]
        output = [s for s in records if s.startswith(self.report_matches)]

        self.assertListEqual(expected, output)

    def test_check_for_invalid_strings_po_missing_header(self):
        ReportManager.getEnabledReporters()[0].reports = []

        path = join(self.path, "missing_header")
        language_path = join(path, "resources", "language", "resource.language.en_gb")
        full_path = join(language_path, "strings.po")

        file_index = [{"path": language_path, "name": "strings.po"}]

        expected = [f'ERROR: Invalid PO file { relative_path(full_path) }:\n'
                    'Missing required header:\n'
                    '\tmsgid ""\n\tmsgstr ""']

        check_for_invalid_strings_po(self.report, file_index)

        records = [Record.__str__(r) for r in ReportManager.getEnabledReporters()[0].reports]
        output = [s for s in records if s.startswith(self.report_matches)]

        self.assertListEqual(expected, output)

    def test_check_for_invalid_strings_po_syntax_error(self):
        ReportManager.getEnabledReporters()[0].reports = []

        path = join(self.path, "syntax_error")
        language_path = join(path, "resources", "language", "resource.language.en_gb")
        full_path = join(language_path, "strings.po")

        file_index = [{"path": language_path, "name": "strings.po"}]

        expected = [f"ERROR: Invalid PO file { relative_path(full_path) }: "
                    "Syntax error on line 23"]

        check_for_invalid_strings_po(self.report, file_index)

        records = [Record.__str__(r) for r in ReportManager.getEnabledReporters()[0].reports]
        output = [s for s in records if s.startswith(self.report_matches)]

        self.assertListEqual(expected, output)

    def test_check_for_invalid_strings_po_encoding(self):
        ReportManager.getEnabledReporters()[0].reports = []

        path = join(self.path, "encoding")
        language_path = join(path, "resources", "language", "resource.language.en_gb")
        full_path = join(language_path, "strings.po")

        file_index = [{"path": language_path, "name": "strings.po"}]

        expected = [f"ERROR: Invalid PO file { relative_path(full_path) }: "
                    "File is not saved with UTF-8 encoding"]

        check_for_invalid_strings_po(self.report, file_index)

        records = [Record.__str__(r) for r in ReportManager.getEnabledReporters()[0].reports]
        output = [s for s in records if s.startswith(self.report_matches)]

        self.assertListEqual(expected, output)

    def test_check_for_invalid_strings_po_bom(self):
        ReportManager.getEnabledReporters()[0].reports = []

        path = join(self.path, "bom")
        language_path = join(path, "resources", "language", "resource.language.en_gb")
        full_path = join(language_path, "strings.po")

        file_index = [{"path": language_path, "name": "strings.po"}]

        expected = [f"ERROR: Invalid PO file { relative_path(full_path) }: "
                    "File contains BOM (byte order mark)"]

        check_for_invalid_strings_po(self.report, file_index)

        records = [Record.__str__(r) for r in ReportManager.getEnabledReporters()[0].reports]
        output = [s for s in records if s.startswith(self.report_matches)]

        self.assertListEqual(expected, output)

    def test_check_for_invalid_strings_po_empty(self):
        ReportManager.getEnabledReporters()[0].reports = []

        path = join(self.path, "empty")
        language_path = join(path, "resources", "language", "resource.language.en_gb")
        full_path = join(language_path, "strings.po")

        file_index = [{"path": language_path, "name": "strings.po"}]

        expected = [f"ERROR: Invalid PO file { relative_path(full_path) }: File is empty"]

        check_for_invalid_strings_po(self.report, file_index)

        records = [Record.__str__(r) for r in ReportManager.getEnabledReporters()[0].reports]
        output = [s for s in records if s.startswith(self.report_matches)]

        self.assertListEqual(expected, output)

    def test_check_for_invalid_strings_po_language_code(self):
        ReportManager.getEnabledReporters()[0].reports = []

        path = join(self.path, "path_check")
        language_path = join(path, "resources", "language")

        file_index = [{"path": join(language_path, "resource.language.testing"), "name": "strings.po"},
                      {"path": join(language_path, "resource.language.en_gb"), "name": "strings.po"}]

        expected = [
            "ERROR: PO file with invalid language code in the correct path: " \
            f"{ relative_path(join(language_path, 'resource.language.testing', 'strings.po')) }"
        ]

        check_for_invalid_strings_po(self.report, file_index)

        matches = (
            self.report_matches,
            "ERROR: PO file with invalid language code in the correct path"
        )

        records = [Record.__str__(r) for r in ReportManager.getEnabledReporters()[0].reports]
        output = [s for s in records if s.startswith(matches)]

        self.assertListEqual(expected, output)

    def test_check_for_invalid_strings_po_missing_en_gb(self):
        ReportManager.getEnabledReporters()[0].reports = []

        path = join(self.path, "path_check")
        language_path = join(path, "resources", "language")

        file_index = [{"path": join(language_path, "resource.language.en_us"), "name": "strings.po"}]

        expected = [
            "ERROR: Required default language 'en_gb' is not present."
        ]

        check_for_invalid_strings_po(self.report, file_index)

        matches = (
            self.report_matches,
            "ERROR: Required default language",
        )

        records = [Record.__str__(r) for r in ReportManager.getEnabledReporters()[0].reports]
        output = [s for s in records if s.startswith(matches)]
        self.assertListEqual(expected, output)
