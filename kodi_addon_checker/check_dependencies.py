"""
    Copyright (C) 2017-2018 Team Kodi
    This file is part of Kodi - kodi.tv

    SPDX-License-Identifier: GPL-3.0-only
    See LICENSES/README.md for more information.
"""

from .addons.Addon import Addon

import logging
from distutils.version import LooseVersion

from .report import Report
from .record import PROBLEM, Record, WARNING, INFORMATION

common_ignore_deps = ['xbmc.metadata.scraper.albums', 'xbmc.metadata.scraper.movies',
                      'xbmc.metadata.scraper.musicvideos', 'xbmc.metadata.scraper.tvshows',
                      'xbmc.metadata.scraper.library', 'xbmc.ui.screensaver', 'xbmc.player.musicviz',
                      'xbmc.python.pluginsource', 'xbmc.python.script', 'xbmc.python.weather', 'xbmc.python.lyrics',
                      'xbmc.python.library', 'xbmc.python.module', 'xbmc.subtitle.module', 'kodi.context.item',
                      'kodi.game.controller', 'xbmc.gui.skin', 'xbmc.webinterface', 'xbmc.addon.repository',
                      'xbmc.pvrclient', 'kodi.gameclient', 'kodi.peripheral', 'kodi.resource', 'xbmc.addon.video',
                      'xbmc.addon.audio', 'xbmc.addon.image', 'xbmc.addon.executable', 'kodi.addon.game',
                      'kodi.audioencoder', 'kodi.audiodecoder', 'xbmc.service', 'kodi.resource.images',
                      'kodi.resource.language', 'kodi.resource.uisounds', 'kodi.resource.games',
                      'kodi.resource.font', 'kodi.inputstream', 'kodi.vfs', 'kodi.imagedecoder', 'xbmc.addon',
                      'xbmc.gui', 'xbmc.json', 'xbmc.metadata', 'xbmc.python', 'script.module.pil']

VERSION_ATTRB = {'xbmc.python': {'gotham': '2.14.0', 'helix': '2.19.0', 'isengard': '2.20.0',
                                 'jarvis': '2.24.0', 'krypton': '2.25.0', 'leia': '2.26.0'}}

LOGGER = logging.getLogger(__name__)


def check_addon_dependencies(report: Report, repo_addons: dict, parsed_xml, branch_name: str):
    """Check for any new dependencies in addon.xml file and reports them
        :parsed_xml: parsed addon.xml file
        :repo_addons: dictionary having all the addon list of a particular
                        version of kodi
        :branch_name: name of the kodi branch/version
    """

    addon = Addon(parsed_xml)
    ignore = _get_ignore_list(branch_name)

    for dependency in addon.dependencies:
        if dependency.id in ignore and not dependency.optional:
            pass

        elif dependency.id not in repo_addons:
            report.add(Record(INFORMATION if dependency.optional else PROBLEM,
                              "{} dependency {} is not available in current repository"
                              .format("Optional" if dependency.optional else "Required", dependency.id)))

        elif dependency.version is None:
            report.add(Record(INFORMATION if dependency.optional else WARNING,
                              "{} dependency {} does not require a minimum version, available: {}"
                              .format("Optional" if dependency.optional else "Required", dependency.id,
                                      repo_addons.find(dependency.id).version)))

        elif repo_addons.find(dependency.id).version < dependency.version:
            report.add(Record(INFORMATION if dependency.optional else PROBLEM,
                              "Version mismatch for {} dependency {}, required: {}, Available: {}"
                              .format("optional" if dependency.optional else "required", dependency.id,
                                      dependency.version, repo_addons.find(dependency.id).version)))

        if dependency.id in VERSION_ATTRB:
            try:
                version = VERSION_ATTRB[dependency.id][branch_name]
                if LooseVersion(version) != dependency.version:
                    report.add(Record(WARNING, "For {} it is advised to set {} version to {}"
                                      .format(branch_name, dependency.id, version)))
            except KeyError:
                LOGGER.warn("Misconfiguration in VERSION_ATTRB of check_dependencies")


def _get_ignore_list(branch_name):

    if branch_name == "leia":
        common_ignore_deps.extend(["script.module.pycryptodome"])
        return common_ignore_deps

    elif branch_name == "krypton":
        common_ignore_deps.extend(["inputstream.adaptive", "inputstream.rtmp"])
        return common_ignore_deps

    else:
        return common_ignore_deps
