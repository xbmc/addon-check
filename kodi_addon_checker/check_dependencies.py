"""
    Copyright (C) 2017-2018 Team Kodi
    This file is part of Kodi - kodi.tv

    SPDX-License-Identifier: GPL-3.0-only
    See LICENSES/README.md for more information.
"""

import logging

from .addons.Addon import Addon
from .record import INFORMATION, PROBLEM, WARNING, Record
from .report import Report
from .versions import AddonVersion, KodiVersion


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
                      'xbmc.gui', 'xbmc.json', 'xbmc.metadata', 'xbmc.python', 'script.module.pil',
                      'kodi.binary.global.main', 'kodi.binary.global.audioengine', 'kodi.binary.global.filesystem',
                      'kodi.binary.global.general', 'kodi.binary.global.gui', 'kodi.binary.global.main',
                      'kodi.binary.global.network', 'kodi.binary.global.tools', 'kodi.binary.instance.audiodecoder',
                      'kodi.binary.instance.audioencoder', 'kodi.binary.instance.game',
                      'kodi.binary.instance.imagedecoder', 'kodi.binary.instance.inputstream',
                      'kodi.binary.instance.peripheral', 'kodi.binary.instance.pvr', 'kodi.binary.instance.screensaver',
                      'kodi.binary.instance.vfs', 'kodi.binary.instance.videocodec',
                      'kodi.binary.instance.visualization']

extensions = {"kodi.gameclient": "kodi.binary.instance.game",
              "xbmc.gui.skin": "xbmc.gui",
              "kodi.vfs": "kodi.binary.instance.vfs",
              "xbmc.metadata.scraper.albums": "xbmc.metadata",
              "xbmc.metadata.scraper.artists": "xbmc.metadata",
              "xbmc.metadata.scraper.library": "xbmc.metadata",
              "xbmc.metadata.scraper.movies": "xbmc.metadata",
              "xbmc.metadata.scraper.musicvideos": "xbmc.metadata",
              "xbmc.metadata.scraper.tvshows": "xbmc.metadata",
              "xbmc.pvrclient": "kodi.binary.instance.pvr",
              "xbmc.python.library": "xbmc.python",
              "xbmc.python.lyrics": "xbmc.python",
              "xbmc.python.module": "xbmc.python",
              "xbmc.python.pluginsource": "xbmc.python",
              "xbmc.python.script": "xbmc.python",
              "xbmc.python.weather": "xbmc.python",
              "xbmc.ui.screensaver": "xbmc.python",
              "xbmc.webinterface": "xbmc.webinterface",
              }

VERSION_ATTRB = {
    'xbmc.python': {
        'gotham': {'min_compatible': '2.1.0', 'advised': '2.14.0'},
        'helix': {'min_compatible': '2.1.0', 'advised': '2.19.0'},
        'isengard': {'min_compatible': '2.1.0', 'advised': '2.20.0'},
        'jarvis': {'min_compatible': '2.1.0', 'advised': '2.24.0'},
        'krypton': {'min_compatible': '2.1.0', 'advised': '2.25.0'},
        'leia': {'min_compatible': '2.1.0', 'advised': '2.26.0'},
        'matrix': {'min_compatible': '3.0.0', 'advised': '3.0.0'}
    },
    'xbmc.gui': {
        'gotham': {'min_compatible': '5.0.0', 'advised': '5.0.0'},
        'helix': {'min_compatible': '5.3.0', 'advised': '5.3.0'},
        'isengard': {'min_compatible': '5.3.0', 'advised': '5.9.0'},
        'jarvis': {'min_compatible': '5.10.0', 'advised': '5.10.0'},
        'krypton': {'min_compatible': '5.12.0', 'advised': '5.12.0'},
        'leia': {'min_compatible': '5.14.0', 'advised': '5.14.0'},
        'matrix': {'min_compatible': '5.14.0', 'advised': '5.15.0'}
    },
    'xbmc.json': {
        'gotham': {'min_compatible': '6.0.0', 'advised': '5.0.0'},
        'helix': {'min_compatible': '6.0.0', 'advised': '6.20.0'},
        'isengard': {'min_compatible': '6.0.0', 'advised': '6.25.1'},
        'jarvis': {'min_compatible': '6.0.0', 'advised': '6.32.4'},
        'krypton': {'min_compatible': '6.0.0', 'advised': '7.0.0'},
        'leia': {'min_compatible': '6.0.0', 'advised': '9.7.2'},
        'matrix': {'min_compatible': '6.0.0', 'advised': '11.2.0'}
    },
    'xbmc.addon': {
        'gotham': {'min_compatible': '12.0.0', 'advised': '13.0.0'},
        'helix': {'min_compatible': '12.0.0', 'advised': '14.0.0'},
        'isengard': {'min_compatible': '12.0.0', 'advised': '15.0.0'},
        'jarvis': {'min_compatible': '12.0.0', 'advised': '16.0.0'},
        'krypton': {'min_compatible': '12.0.0', 'advised': '17.0.0'},
        'leia': {'min_compatible': '12.0.0', 'advised': '17.9.910'},
        'matrix': {'min_compatible': '12.0.0', 'advised': '18.9.701'}
    },
    'xbmc.metadata': {
        'gotham': {'min_compatible': '1.0', 'advised': '2.1.0'},
        'helix': {'min_compatible': '1.0', 'advised': '2.1.0'},
        'isengard': {'min_compatible': '1.0', 'advised': '2.1.0'},
        'jarvis': {'min_compatible': '1.0', 'advised': '2.1.0'},
        'krypton': {'min_compatible': '1.0', 'advised': '2.1.0'},
        'leia': {'min_compatible': '1.0', 'advised': '2.1.0'},
        'matrix': {'min_compatible': '1.0', 'advised': '2.1.0'}
    },
}

LOGGER = logging.getLogger(__name__)


def check_addon_dependencies(report: Report, repo_addons: dict, parsed_xml, args):
    """Check for any new dependencies in addon.xml file and reports them
        :parsed_xml: parsed addon.xml file
        :repo_addons: dictionary having all the addon list of a particular
                        version of kodi
        :args: the args object passed to addon-checker
    """

    addon = Addon(parsed_xml)
    ignore = _get_ignore_list(KodiVersion(args.branch))
    pr = bool(args.PR)

    for dependency in addon.dependencies:
        if dependency.id in ignore and not dependency.optional:
            pass

        elif dependency.id not in repo_addons:
            if dependency.optional:
                record_level = INFORMATION
            elif not pr:
                record_level = WARNING
            else:
                record_level = PROBLEM

            report.add(Record(record_level,
                              "{} dependency {} is not available in current repository"
                              .format("Optional" if dependency.optional else "Required", dependency.id)))

        elif dependency.version is None:
            report.add(Record(INFORMATION if dependency.optional else WARNING,
                              "{} dependency {} does not require a minimum version, available: {}"
                              .format("Optional" if dependency.optional else "Required", dependency.id,
                                      repo_addons.find(dependency.id).version)))

        elif AddonVersion(repo_addons.find(dependency.id).version) < dependency.version:
            report.add(Record(INFORMATION if dependency.optional else PROBLEM,
                              "Version mismatch for {} dependency {}, required: {}, Available: {}"
                              .format("optional" if dependency.optional else "required", dependency.id,
                                      dependency.version, repo_addons.find(dependency.id).version)))

        if dependency.id in VERSION_ATTRB:
            try:
                version_info = VERSION_ATTRB[dependency.id][args.branch]
                if AddonVersion(version_info["min_compatible"]) > dependency.version:
                    report.add(Record(PROBLEM, "For {}, {} version must be higher than {}. Advised {}."
                                      .format(args.branch, dependency.id,
                                              version_info["min_compatible"], version_info["advised"])))
                    continue

                if AddonVersion(version_info["advised"]) != dependency.version:
                    report.add(Record(WARNING, "For {} it is advised to set {} version to {}"
                                      .format(args.branch, dependency.id, version_info["advised"])))

            except KeyError:
                LOGGER.warning("Misconfiguration in VERSION_ATTRB of check_dependencies")

    _check_extensions(report, parsed_xml, addon)


def check_reverse_dependencies(report: Report, addon: str, branch_name: str, all_repo_addons: dict):
    """Check for orphaned addon i.e the addons that are not requirement of any other addon.

      :addon: addon that is to be checked
      :branch_name: name of the branch on which the
                    checks are being performed
      :all_repo_addons: a nested list having information
                        about all the repo addonst
    """
    addonInRepo = None
    rdepends = []
    rdependsLowerBranch = []
    branchFound = False

    for branch, repo in sorted(all_repo_addons.items()):
        if not branchFound and branch != branch_name:
            for rdepend in repo.rdepends(addon):
                if rdepend not in rdependsLowerBranch:
                    rdependsLowerBranch.append(rdepend)
            continue
        branchFound = True

        addonFind = repo.find(addon)
        if addonFind and addonInRepo and addonFind != addonInRepo:
            break

        addonInRepo = addonFind

        for rdepend in repo.rdepends(addon):
            if rdepend not in rdependsLowerBranch and rdepend not in rdepends:
                rdepends.append(rdepend)
    if addon.startswith("script.module.") and len(rdepends) + len(rdependsLowerBranch) == 0:
        report.add(Record(WARNING, "This module isn't required by any add-on."))

    if rdepends:
        report.add(Record(INFORMATION, "Reverse dependencies: {} ({})"
                          .format(", ".join(sorted([r.id for r in rdepends])), len(rdepends))))

    if rdependsLowerBranch:
        report.add(Record(INFORMATION, "Reverse dependencies (in lower branches): {} ({})"
                          .format(", ".join(sorted([r.id for r in rdependsLowerBranch])), len(rdependsLowerBranch))))


def _get_ignore_list(kodi_version: KodiVersion):
    """Generate an dependency ignore list based
       on the branch name
    """

    if kodi_version >= KodiVersion("leia"):
        common_ignore_deps.extend(["script.module.pycryptodome"])

    if kodi_version == KodiVersion("krypton"):
        common_ignore_deps.extend(["inputstream.adaptive", "inputstream.rtmp"])

    return common_ignore_deps


def _check_extensions(report: Report, parsed_xml, addon):
    """Check if required dependency exist with comparision to
       the existing extension points

      :addon: class kodi_addon_checker.addons.Addon.Addon
    """
    deps = [dependency.id for dependency in addon.dependencies]

    for extension in parsed_xml.findall("extension"):
        point = extension.get("point")
        if point in extensions and extensions[point] not in deps:
            report.add(Record(PROBLEM, "{} dependency is required for {} extensions"
                              .format(extensions[point], point)))
