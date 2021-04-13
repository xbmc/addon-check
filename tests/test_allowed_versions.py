# -*- coding: utf-8 -*-
#

from kodi_addon_checker.check_allowed_versions import version_is_valid

def test_addonversion_simple():
    assert version_is_valid("1.0.1")


def test_addonversion_localversionidentifier():
    assert version_is_valid("1.0.1+matrix.1")


def test_addonversion_localversionidentifier2():
    assert version_is_valid("1.0.1+matrix.2")


def test_invalidversion():
    assert not version_is_valid("someinvalidversion")


def test_invalidbackportversion():
    assert not version_is_valid("2.3.0-backported-Leia")
