import unittest
from os.path import abspath, dirname, join

from kodi_addon_checker.check_files import check_file_permission
from kodi_addon_checker.handle_files import create_file_index

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
        path = join(HERE, 'test_data', 'Executable_file')
        string = "ERROR: {path} is marked as stand-alone executable"\
            .format(path=relative_path(join(path, "file_permission.py")))
        file_index = create_file_index(path)
        check_file_permission(self.report, file_index)
        records = [Record.__str__(r) for r in ReportManager.getEnabledReporters()[0].reports]
        flag = any(s == string for s in records)
        self.assertTrue(flag)

    def test_check_file_permission_is_None(self):
        path = join(HERE, 'test_data', 'Non-Executable_file')
        file_index = create_file_index(path)
        self.assertIsNone(check_file_permission(self.report, file_index))
