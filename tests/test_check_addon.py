import unittest
from kodi_addon_checker.check_addon import get_all_repo_addons
from kodi_addon_checker.check_addon import start
from kodi_addon_checker.common import load_plugins
from kodi_addon_checker.record import Record
from kodi_addon_checker.reporter import ReportManager
from kodi_addon_checker.config import Config


class Args():
    PR = False
    allow_folder_id_mismatch = False
    branch = "krypton"


class TestCheckAddon(unittest.TestCase):
    """Integration tests for Start function present in check_addon.py"""

    def setUp(self):
        self.path = "script.test/"
        self.whitelist = ["INFO: Checking add-on script.test", "INFO: Created by mzfr", "INFO: This is a new addon"
                          "INFO: Image icon exists", "Icon dimensions are fine", "INFO: Image fanart exists",
                          "WARN: Complex entry point", "WARN: We found", "please check the logfile"]
        load_plugins()
        self.config = Config(self.path)
        ReportManager.enable(["array"])
        self.all_repo_addons = get_all_repo_addons()
        self.args = Args()
        self.args.skip_dependency_checks = False

    def test_start(self):
        start(self.path, self.args, self.all_repo_addons, self.config)
        records = [Record.__str__(r) for r in ReportManager.getEnabledReporters()[0].reports]

        # Comparing the whitelist with the list of output we get from addon-checker tool
        for white_str in self.whitelist:
            for value in records:
                if white_str.lower() == value.lower():
                    break
            else:
                flag = False
        else:
            flag = True

        self.assertTrue(flag)
