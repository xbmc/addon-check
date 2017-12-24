# -*- coding: utf-8 -*-
#

import os
import json
import pytest
from common import check_config


def _read_config_for_version(filename):
    config_path = os.path.join("tests\\fixtures", filename)
    if os.path.isfile(config_path):
        with open(config_path) as json_data:
            return json.load(json_data)

    return None



def test_if_false_gets_picked_up():
    config = _read_config_for_version('.tests-config.json')
    assert check_config(config, "check_license_file_exists") is False


def test_if_true_gets_picked_up():
    config = _read_config_for_version('.tests-config.json')
    print(config)
    assert check_config(config, "check_legacy_strings_xml") is True


def test_if_does_not_exists_default_to_false():
    config = _read_config_for_version('.tests-config.json')
    assert check_config(config, "does_not_exist") is False


def test_with_missing_config():
    config = _read_config_for_version('does_not_exist.json')
    assert check_config(config, "does_not_exist") is False
