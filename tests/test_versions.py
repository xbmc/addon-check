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
    assert AddonVersion("1.0.0+leia.1") == AddonVersion("1.0.0+Leia.1")


def test_addonversion_kodi_simplevsstring():
    assert AddonVersion("0.5.4.1") > AddonVersion("0.5.4+matrix.1")


def test_kodi_non_compliant_pep440_builtin_versions():
    # mimics the tests in TestAddonVersion.cpp (non PEP440 compliant)
    # try to use PEP440 compliant versions whenever possible
    assert AddonVersion("1.0.0-1") > AddonVersion("1.0.0")
    assert AddonVersion("1.0.0~beta2") > AddonVersion("1.0.0~beta1")
    assert AddonVersion("1.0.1~beta01") > AddonVersion("1.0.0")
    assert AddonVersion("1.0.1~beta") > AddonVersion("1.0.0")
    assert AddonVersion("1.0.0~beta") > AddonVersion("1.0.0~alpha")
    assert AddonVersion("1.0.0~beta2") > AddonVersion("1.0.0~alpha")
    assert AddonVersion("1.0.0~alpha3") > AddonVersion("1.0.0~alpha2")


def test_kodiversions():
    assert KodiVersion("matrix") > KodiVersion("leia")
