"""
    Copyright (C) 2018 Team Kodi
    This file is part of Kodi - kodi.tv

    SPDX-License-Identifier: GPL-3.0-only
    See LICENSES/README.md for more information.
"""

import atexit
import gzip
import time
import xml.etree.ElementTree as ET
from io import BytesIO

import requests

from .Addon import Addon
from ..versions import AddonVersion


class RateLimitedAdapter(requests.adapters.HTTPAdapter):
    def __init__(self, *args, retries=5, wait=None, **kwargs):
        self._last_send = None
        self._wait_time = wait
        max_retries = requests.adapters.Retry(
            total=retries,
            backoff_factor=wait or 10,
            status_forcelist={429, },
            allowed_methods=None,
        )
        kwargs.setdefault('max_retries', max_retries)
        super().__init__(*args, **kwargs)

    def send(self, *args, **kwargs):
        if self._wait_time and self._last_send:
            delta = time.time() - self._last_send
            if delta < self._wait_time:
                time.sleep(self._wait_time - delta)

        self._last_send = time.time()
        response = super().send(*args, **kwargs)
        status_code = getattr(response, 'status_code', None)
        if 300 <= status_code < 400:
            self._last_send = None
        return response


class Repository():
    # Recover from unreliable mirrors
    _session = requests.Session()
    _adapter = RateLimitedAdapter(retries=5, pool_maxsize=3, pool_block=True)
    _session.mount('http://', _adapter)
    _session.mount('https://', _adapter)
    atexit.register(_session.close)

    def __init__(self, version, path):
        super().__init__()
        self.version = version
        self.path = path

        try:
            response = self._session.get(path, timeout=(30, 30))
            response.raise_for_status()
        except requests.exceptions.RequestException:
            return
        content = response.content

        if path.endswith('.gz'):
            with gzip.open(BytesIO(content), 'rb') as xml_file:
                content = xml_file.read()

        self.addons = []
        tree = ET.fromstring(content)
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
