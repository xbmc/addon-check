"""
    Copyright (C) 2018 Team Kodi
    This file is part of Kodi - kodi.tv

    SPDX-License-Identifier: GPL-3.0-only
    See LICENSES/README.md for more information.
"""

import xml.etree.ElementTree as ET

from .addon_dependency import AddonDependency


class Addon():
    def __init__(self, addon_xml: ET.Element):
        # pylint: disable=invalid-name
        super(Addon, self).__init__()
        self.id = addon_xml.get('id')
        self.version = addon_xml.get('version')
        self.dependencies = []
        for dependency in addon_xml.findall('./requires/import'):
            self.dependencies.append(AddonDependency(dependency))

    def __eq__(self, other):
        return self.id == other.id and self.version == other.version

    def depends_on(self, addon_id):
        for dependency in self.dependencies:
            if dependency.id == addon_id:
                return True
        return False
