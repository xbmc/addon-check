# -*- coding: utf-8 -*-
#

from kodi_addon_checker.versions import AddonVersion, KodiVersion


def test_addonversion_simple_patch():
    assert AddonVersion("1.0.1") > AddonVersion("1.0.0")


def test_addonversion_simple_minor():
    assert AddonVersion("1.1.0") > AddonVersion("1.0.0")


def test_addonversion_simple_major():
    assert AddonVersion("2.0.0") > AddonVersion("1.0.0")


def test_addonversion_kodi_versions():
    assert AddonVersion("1.0.0+matrix.1") > AddonVersion("1.0.0+leia.1")


def test_addonversion_kodi_simplevsstring():
    assert AddonVersion("0.5.4.1") > AddonVersion("0.5.4+matrix.1")


def test_kodiversions():
    assert KodiVersion("matrix") > KodiVersion("leia")
