# -*- coding: utf-8 -*-
#

import os
import json
import pytest
from PIL import Image
from addon_checker.common import check_config, has_transparency

FIXTURE_PATH = os.path.join("tests", "fixtures")


def __read_config_for_version(filename):
    config_path = os.path.join(FIXTURE_PATH, filename)
    if os.path.isfile(config_path):
        with open(config_path) as json_data:
            return json.load(json_data)

    return None


def __load_image(filename):
    filepath = os.path.join(FIXTURE_PATH, filename)
    return Image.open(filepath)


def test_if_false_gets_picked_up():
    config = __read_config_for_version('.tests-config.json')
    assert check_config(config, "check_license_file_exists") is False


def test_if_true_gets_picked_up():
    config = __read_config_for_version('.tests-config.json')
    assert check_config(config, "check_legacy_strings_xml") is True


def test_if_does_not_exists_default_to_false():
    config = __read_config_for_version('.tests-config.json')
    assert check_config(config, "does_not_exist") is False


def test_with_missing_config():
    config = __read_config_for_version('does_not_exist.json')
    assert check_config(config, "does_not_exist") is False


def test_has_transparency_rgb():
    image = __load_image("rgb_icon.png")
    assert has_transparency(image) is False


def test_has_transparency_rgba():
    image = __load_image("rgba_icon.png")
    assert has_transparency(image) is False


def test_has_transparency_rgba_transparency():
    image = __load_image("rgba_icon_transparency.png")
    assert has_transparency(image) is True
