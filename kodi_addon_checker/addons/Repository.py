"""
    Copyright (C) 2018 Team Kodi
    This file is part of Kodi - kodi.tv

    SPDX-License-Identifier: GPL-3.0-only
    See LICENSES/README.md for more information.
"""

import gzip
import xml.etree.ElementTree as ET
from io import BytesIO

import requests

from .Addon import Addon
from ..versions import AddonVersion


class Repository():
    def __init__(self, version, path):
        super().__init__()
        self.version = version
        self.path = path

        # Recover from unreliable mirrors
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=5)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        content = session.get(path, timeout=(30, 30)).content

        if path.endswith('.gz'):
            with gzip.open(BytesIO(content), 'rb') as xml_file:
                content = xml_file.read()

        tree = ET.fromstring(content)
        self.addons = []
        for addon in tree.findall("addon"):
            self.addons.append(Addon(addon))

    def __contains__(self, addonId):
        for addon in self.addons:
            if addon.id == addonId:
                return True
        return False

    def find(self, addonId):
        # multiple copies of the same addon might exist on the repository, however
        # kodi always uses the highest version available
        addon_instances = []
        for addon in self.addons:
            if addon.id == addonId:
                addon_instances.append(addon)

        if not addon_instances:
            return None

        # always return the highest version for the given addon id available in the repo
        addon_instances.sort(key=lambda addon: AddonVersion(addon.version), reverse=True)
        return addon_instances[0]

    def rdepends(self, addonId):
        rdepends = []
        for addon in self.addons:
            if addon.dependsOn(addonId):
                rdepends.append(addon)
        return rdepends
