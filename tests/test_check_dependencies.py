import unittest

from os.path import abspath, dirname, join
import xml.etree.ElementTree as ET

from kodi_addon_checker.addons.Addon import Addon
from kodi_addon_checker.addons.Repository import Repository
from kodi_addon_checker.check_dependencies import check_circular_dependencies
from kodi_addon_checker.check_dependencies import create_dependency_tree
from kodi_addon_checker.common import load_plugins
from kodi_addon_checker.record import Record
from kodi_addon_checker.reporter import ReportManager
from kodi_addon_checker.report import Report

HERE = abspath(dirname(__file__))


class TestCheckDependencies(unittest.TestCase):
    """Test dependency checks
    """

    def setUp(self):
        """Test setup
        """
        load_plugins()
        ReportManager.enable(["array"])
        self.report = Report("")
        self.branch = 'krypton'
        self.path = join(HERE, 'test_data', 'Circular_depend')

    def test_check_circular_dependency(self):
        """Test circular dependency check
        """
        addon_xml = join(self.path, "addon.xml")
        addons_xml = join(self.path, "addons.xml")

        parsed_xml = ET.parse(addon_xml).getroot()
        all_repo_addons = {self.branch: Repository(self.branch, addons_xml)}

        check_circular_dependencies(self.report, all_repo_addons, parsed_xml, self.branch)

        records = [Record.__str__(r) for r in ReportManager.getEnabledReporters()[0].reports]
        output = [record for record in records if record.startswith("ERROR: Circular")]
        expected = ["ERROR: Circular dependencies: plugin.test.one"]

        self.assertListEqual(expected, output)

    def test_dependency_tree_creation(self):
        """Test dependency tree creation
        """
        addon_xml = join(self.path, "addon.xml")
        addons_xml = join(self.path, "addons.xml")

        parsed_xml = ET.parse(addon_xml).getroot()
        addon = Addon(parsed_xml)
        all_repo_addons = {self.branch: Repository(self.branch, addons_xml)}

        output = create_dependency_tree(addon, all_repo_addons, self.branch)
        expected = {'plugin.test.two': ['plugin.test.one'], 'plugin.test.one': ['plugin.test.two']}

        self.assertEqual(expected, output)
