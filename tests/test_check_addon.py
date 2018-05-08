import unittest
from kodi_addon_checker.check_addon import start
from kodi_addon_checker.record import Record
from kodi_addon_checker.config import Config


class TestCheckAddon(unittest.TestCase):
    """Integration tests for Start function present in check_addon.py"""

    def setUp(self):
        self.path = "/home/mzfr/dev/Addon-check/addons/plugin.video.twitch/"
        self.whitelist = ["INFO: checking addon", "INFO: created by",
                          "Image icon", "Icon dimensions are fine", "fanart",
                          "WARN: Complex entry point", "WARN: We found"]
        self.config = Config(self.path)

    def test_start(self):

        result = start(self.path, self.config)
        values = [Record.__str__(r) for r in result]
        self.assertTrue(any(any(x in z for z in values) for x in self.whitelist))
