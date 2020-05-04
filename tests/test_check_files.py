import os
import unittest
from os.path import abspath, dirname, join

from kodi_addon_checker.check_files import check_file_permission, check_file_whitelist
from kodi_addon_checker.handle_files import create_file_index

from kodi_addon_checker.common import load_plugins, relative_path, get_debug_log_path, get_reporter_log_path
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
        if os.name == "nt":
            self.assertFalse(flag)
        else:
            self.assertTrue(flag)

    def test_check_file_permission_is_None(self):
        path = join(HERE, 'test_data', 'Non-Executable_file')
        file_index = create_file_index(path)
        self.assertIsNone(check_file_permission(self.report, file_index))


class TestCheckFileWhitelist(unittest.TestCase):
    """Use cases:
        - Ignore the log files if they are generated in the folder that is
        being checked
        - Report the files which have the same name as the log files but that
        are not generated in this run of the checker
        - Report the log files in the current folder if one/both reporter(s)
        is/are disabled
    """

    def setUp(self):
        # General initializaiton
        load_plugins()
        ReportManager.enable(["array"])
        self.report = Report("")

        # Create a dummy path not containing ".module." so that the check is
        # not skipped
        self.addon_path = "script.test"

        # Get the name of the log files
        self.debug_log_filename = os.path.basename(get_debug_log_path())
        self.reporter_log_filename = os.path.basename(get_reporter_log_path())

        # Create the file index from the "script.test" folder
        script_test_path = join(HERE, "..", 'script.test')
        self.file_index = create_file_index(script_test_path)
        # The log files are supposed to be generated in the folder being
        # checked so add them to the file index but stub the path to be in the
        # current folder (since the log files are supposed to be generated there)
        self.file_index.append({"path": os.path.dirname(get_debug_log_path()),
                                "name": self.debug_log_filename})
        self.file_index.append({"path": os.path.dirname(get_reporter_log_path()),
                               "name": self.reporter_log_filename})

    def check_if_log_files_were_reported(self):
        """Helper function to check if the log files were reported."""

        # Initialize the returned values
        debug_log_reported = False
        reporter_log_reported = False

        # For each records generated check if the name of the log files was mentioned
        for r in ReportManager.getEnabledReporters()[0].reports:
            # Convert the record to a string
            record = Record.__str__(r)
            # Check if the log files name is in the record
            if self.debug_log_filename in record:
                debug_log_reported = True
            elif self.reporter_log_filename in record:
                reporter_log_reported = True
            # Note: "elif" is used to improve performance because we assume only 1
            # log file may exist in a give record

        # Resert the report so that the next test case starts fresh
        ReportManager.getEnabledReporters()[0].reports = []

        return debug_log_reported, reporter_log_reported

    def test_check_file_whitelist_both_log_files_enabled(self):
        """Test "check_file_whitelist" when both log files are enabled.

        The log files must be ignored because they are being generated in the
        folder that is being analyzed.
        """

        # Call the function with both logs enabled
        check_file_whitelist(self.report, self.file_index, self.addon_path, True, True)

        # Check if the log files were reported
        debug_log_reported, reporter_log_reported = self.check_if_log_files_were_reported()

        # Only the reporter log file must have been reported
        self.assertFalse(debug_log_reported)
        self.assertFalse(reporter_log_reported)

    def test_check_file_whitelist_debug_log_file_enabled(self):
        """Test "check_file_whitelist" when only the debug log is enabled.

        The debug log file must be ignored but if a file having the same as the
        reporter log exists it must be reported.
        """

        # Call the function with only the debug log enabled
        check_file_whitelist(self.report, self.file_index, self.addon_path, True, False)

        # Check if the log files were reported
        debug_log_reported, reporter_log_reported = self.check_if_log_files_were_reported()

        # Only the reporter log file must have been reported
        self.assertFalse(debug_log_reported)
        self.assertTrue(reporter_log_reported)

    def test_check_file_whitelist_reporter_log_file_enabled(self):
        """Test "check_file_whitelist" when only the reporter log is enabled.

        The reporter log file must be ignored but if a file having the same as
        the reporter log exists it must be reported.
        """

        # Call the function with only the reporter log enabled
        check_file_whitelist(self.report, self.file_index, self.addon_path, False, True)

        # Check if the log files were reported
        debug_log_reported, reporter_log_reported = self.check_if_log_files_were_reported()

        # Only the reporter log file must have been reported
        self.assertTrue(debug_log_reported)
        self.assertFalse(reporter_log_reported)

    def test_check_file_whitelist_log_files_disabled(self):
        """Test "check_file_whitelist" when both log files are disabled.

        The log files must be reported because they are being generated in the
        folder that is being analyzed.
        This use case validates also when the log files are generated out of
        the analyzed folder but there are files with the same names in the
        analyzed folder.
        """

        # Call the function with only the reporter log enabled
        check_file_whitelist(self.report, self.file_index, self.addon_path, False, False)

        # Check if the log files were reported
        debug_log_reported, reporter_log_reported = self.check_if_log_files_were_reported()

        # Only the reporter log file must have been reported
        self.assertTrue(debug_log_reported)
        self.assertTrue(reporter_log_reported)
