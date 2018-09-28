# -*- coding: utf-8 -*-
#

import os

from PIL import Image

from kodi_addon_checker.common import has_transparency
from kodi_addon_checker.config import Config

FIXTURE_PATH = os.path.join("tests", "fixtures")


def __load_image(filename):
    filepath = os.path.join(FIXTURE_PATH, filename)
    return Image.open(filepath)


def test_if_false_gets_picked_up():
    config = Config(FIXTURE_PATH)
    assert config.is_enabled("check_license_file_exists") is False


def test_if_true_gets_picked_up():
    config = Config(FIXTURE_PATH)
    assert config.is_enabled("true_config") is True


def test_if_does_not_exists_default_to_false():
    config = Config(FIXTURE_PATH)
    assert config.is_enabled("does_not_exist") is False


def test_with_missing_config():
    config = Config('does_not_exist')
    assert config.is_enabled("does_not_exist") is False


def test_has_transparency_rgb():
    image = __load_image("rgb_icon.png")
    assert has_transparency(image) is False


def test_has_transparency_rgba():
    image = __load_image("rgba_icon.png")
    assert has_transparency(image) is False


def test_has_transparency_rgba_transparency():
    image = __load_image("rgba_icon_transparency.png")
    assert has_transparency(image) is True
