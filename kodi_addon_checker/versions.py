"""
    Copyright (C) 2019 Team Kodi
    This file is part of Kodi - kodi.tv

    SPDX-License-Identifier: GPL-3.0-only
    See LICENSES/README.md for more information.
"""

from packaging.version import parse, Version, LegacyVersion
from kodi_addon_checker import ValidKodiVersions


class AddonVersion():
    def __init__(self, version):
        self.version = parse(str(version).lower())
        # non PEP440 compliant versions (legacy), for beta and alpha versions
        # convert them into PEP440 format: 1.1.0~beta01 -> 1.1.0beta01
        if self._islegacy_devversion:
            self.version = Version(version.replace("~", ""))

    @property
    def _islegacy_devversion(self):
        return isinstance(self.version, LegacyVersion) and \
            ("~beta" or "~alpha" in self.version)

    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError()
        return self.version < other.version

    def __le__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError()
        return self.version <= other.version

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.version == other.version

    def __ne__(self, other):
        return not isinstance(other, self.__class__) or self.version != other.version

    def __gt__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError()
        return self.version > other.version

    def __ge__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError()
        return self.version >= other.version

    def __repr__(self):
        return str(self.version)


class KodiVersion():
    def __init__(self, version: str):
        if version not in ValidKodiVersions:
            raise ValueError("Invalid KodiVersion")
        super().__init__()
        self.version = version

    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError()
        return ValidKodiVersions.index(self.version) < ValidKodiVersions.index(other.version)

    def __le__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError()
        return ValidKodiVersions.index(self.version) <= ValidKodiVersions.index(other.version)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.version == other.version

    def __ne__(self, other):
        return not isinstance(other, self.__class__) or self.version != other.version

    def __gt__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError()
        return ValidKodiVersions.index(self.version) > ValidKodiVersions.index(other.version)

    def __ge__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError()
        return ValidKodiVersions.index(self.version) >= ValidKodiVersions.index(other.version)

    def __repr__(self):
        return str(self.version)
