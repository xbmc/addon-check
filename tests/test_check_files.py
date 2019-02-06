import unittest
from pathlib import Path
from os import makedirs
from os.path import abspath, dirname, join

from kodi_addon_checker.check_files import check_file_permission
from kodi_addon_checker.check_files import check_file_whitelist
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
        self.path = join(HERE, 'test_data', 'Executable file')
        self.string = "ERROR: {path} is marked as stand-alone executable"\
            .format(path=relative_path(join(self.path, "file_permission.py")))
        file_index = create_file_index(self.path)
        check_file_permission(self.report, file_index, [], [])
        records = [Record.__str__(r) for r in ReportManager.getEnabledReporters()[0].reports]
        flag = any(s == self.string for s in records)
        self.assertTrue(flag)

    def test_check_file_permission_is_None(self):
        self.path = join(HERE, 'test_data', 'Non-Executable file')
        file_index = create_file_index(self.path)
        self.assertIsNone(check_file_permission(self.report, file_index, [], []))

    def test_check_file_permission_is_excluded_by_name(self):
        self.path = join(HERE, 'test_data', 'Executable file')
        self.string = "ERROR: {path} is marked as stand-alone executable"\
            .format(path=relative_path(join(self.path, "file_permission.py")))
        file_index = create_file_index(self.path)
        check_file_permission(self.report, file_index, ["file_permission.py"], [])
        records = [Record.__str__(r) for r in ReportManager.getEnabledReporters()[0].reports]
        flag = any(s == self.string for s in records)
        self.assertFalse(flag)

    def test_check_file_permission_is_excluded_by_ext(self):
        self.path = join(HERE, 'test_data', 'Executable file')
        self.string = "ERROR: {path} is marked as stand-alone executable"\
            .format(path=relative_path(join(self.path, "file_permission.py")))
        file_index = create_file_index(self.path)
        check_file_permission(self.report, file_index, [], ["py"])
        records = [Record.__str__(r) for r in ReportManager.getEnabledReporters()[0].reports]
        flag = any(s == self.string for s in records)
        self.assertFalse(flag)

    def test_check_file_whitelist_is_true(self):
        self.path = join(HERE, 'test_data', 'File whitelist')
        self.string = "WARN: Found non whitelisted file ending in filename {path}"\
            .format(path=relative_path(join(self.path, "file_whitelist.ext")))
        file_index = create_file_index(self.path)
        check_file_whitelist(self.report, file_index, self.path, [], [])
        records = [Record.__str__(r) for r in ReportManager.getEnabledReporters()[0].reports]
        flag = any(s == self.string for s in records)
        self.assertTrue(flag)

    def test_check_file_whitelist_is_excluded_by_name(self):
        self.path = join(HERE, 'test_data', 'File whitelist')
        self.string = "WARN: Found non whitelisted file ending in filename {path}"\
            .format(path=relative_path(join(self.path, "file_whitelist.ext")))
        file_index = create_file_index(self.path)
        check_file_whitelist(self.report, file_index, self.path, ["file_whitelist.ext"], [])
        records = [Record.__str__(r) for r in ReportManager.getEnabledReporters()[0].reports]
        flag = any(s == self.string for s in records)
        self.assertFalse(flag)

    def test_check_file_whitelist_is_excluded_by_ext(self):
        self.path = join(HERE, 'test_data', 'File whitelist')
        self.string = "WARN: Found non whitelisted file ending in filename {path}"\
            .format(path=relative_path(join(self.path, "file_whitelist.ext")))
        file_index = create_file_index(self.path)
        check_file_whitelist(self.report, file_index, self.path, [], ["ext"])
        records = [Record.__str__(r) for r in ReportManager.getEnabledReporters()[0].reports]
        flag = any(s == self.string for s in records)
        self.assertFalse(flag)
