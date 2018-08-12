import unittest
import tempfile
import shutil
from pathlib import Path
from os import makedirs
from os.path import abspath, dirname, join

from kodi_addon_checker.handle_files import find_file
from kodi_addon_checker.handle_files import create_file_index
from kodi_addon_checker.handle_files import find_files_recursive as FFR

HERE = abspath(dirname(__file__))


class TestFindFile(unittest.TestCase):

    def setUp(self):
        self.path = tempfile.mkdtemp()
        self.file = join(self.path, "addon.txt")

    def test_find_file_is_none(self):
        self.assertIsNone(find_file("randomname", self.path))

    def test_find_file_is_not_none(self):
        with open(self.file, "w+"):
            self.assertIsNotNone(find_file("addon.txt", self.path))

    def teardown(self):
        shutil.rmtree(self.path)


class TestFindFilesRecursive(unittest.TestCase):

    def setUp(self):
        self.path = tempfile.mkdtemp()
        self.file = join(self.path, "addon.txt")
        self.dirs = join(self.path, "tree/subdir")
        makedirs(self.dirs)
        self.folder = join(self.dirs, "addon.xml")

    def test_find_files_recursive_is_False(self):
        self.assertFalse(list(FFR("randomname", self.path)))

    def test_find_files_recursive_is_True(self):
        with open(self.file, "w+"):
            self.assertTrue(FFR("addon.txt", self.path))

    def test_find_files_recursive_deeply(self):
        with open(self.folder, "w+"):
            self.assertTrue(FFR("addon.xml", self.path))

    def teardown(self):
        shutil.rmtree(self.path)
        shutil.rmtree(self.folder)


class TestCreateFileIndex(unittest.TestCase):

    def test_create_file_index(self):
        self.path = join(HERE, 'test_data', 'File_index/')
        self.list = [{'path': self.path, 'name': 'file_index.py'}]
        self.output = create_file_index(self.path)
        self.assertListEqual(self.output, self.list)
