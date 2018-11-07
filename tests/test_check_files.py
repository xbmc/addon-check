import unittest
from pathlib import Path
from os import makedirs
from os.path import abspath, dirname, join

from kodi_addon_checker.check_files import check_file_permission

from kodi_addon_checker.common import load_plugins
from kodi_addon_checker.common import relative_path
from kodi_addon_checker.record import Record
from kodi_addon_checker.reporter import ReportManager
from kodi_addon_checker.report import Report


HERE = abspath(dirname(__file__))


class TestCheckFilePermission(unittest.TestCase):

    def setUp(self):
        load_plugins()
        ReportManager.enable(["array"])
        self.report = Report("")

    def test_check_file_permission_is_true(self):
        self.path = join(HERE, 'test_data', 'Executable file')
        self.string = "ERROR: .{path}/file_permission.py is marked as stand-alone executable".format(path=self.path)
        check_file_permission(self.report, self.path)
        records = [Record.__str__(r) for r in ReportManager.getEnabledReporters()[0].reports]
        flag = any(s == self.string for s in records)
        self.assertTrue(flag)

    def test_check_file_permission_is_None(self):
        self.path = join(HERE, 'test_data', 'Non-Executable file')
        self.assertIsNone(check_file_permission(self.report, self.path))
