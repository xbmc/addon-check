import unittest
from kodi_addon_checker.check_addon import all_repo_addons
from kodi_addon_checker.check_addon import start
from kodi_addon_checker.record import Record
from kodi_addon_checker.config import Config


class TestCheckAddon(unittest.TestCase):
    """Integration tests for Start function present in check_addon.py"""

    def setUp(self):
        self.path = "script.test/"
        self.whitelist = ["INFO: Checking add-on script.test", "INFO: Created by mzfr", "INFO: This is a new addon"
                          "INFO: Image icon exists", "Icon dimensions are fine", "INFO: Image fanart exists",
                          "WARN: Complex entry point", "WARN: We found", "please check the logfile"]
        self.config = Config(self.path)
        self.branch_name = "krypton"
        self.all_repo_addons = all_repo_addons()

    def test_start(self):
        result = start(self.path, self.branch_name, self.all_repo_addons, self.config)
        records = [Record.__str__(r) for r in result]

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
