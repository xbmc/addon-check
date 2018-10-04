import logging
from distutils.version import LooseVersion

from .report import Report
from .record import PROBLEM, Record, WARNING

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

    deps = _get_users_dependencies(parsed_xml)
    ignore = _get_ignore_list(branch_name)

    for required_addon, required_version in deps.items():
        if required_addon not in repo_addons:
            if required_addon not in ignore:
                report.add(Record(
                    PROBLEM, "Required addon %s not available in current repository." % required_addon))
            elif required_addon in VERSION_ATTRB:
                try:
                    version = VERSION_ATTRB[required_addon][branch_name]
                    if LooseVersion(version) != LooseVersion(required_version):
                        report.add(Record(WARNING, "For %s it is advised to set %s version to %s" %
                                          (branch_name, required_addon, version)))
                except KeyError:
                    LOGGER.warn("Misconfiguration in VERSION_ATTRB of check_dependencies")

        else:
            available_version = repo_addons[required_addon]

            if required_version is None:
                report.add(Record(WARNING, "Required addon %s does not require a fixed version Available: %s "
                                  % (required_addon, available_version)))
            elif available_version is None:
                report.add(Record(PROBLEM, "Version of %s in required version %s not available"
                                  % (required_addon, required_version)))
            elif LooseVersion(available_version) < LooseVersion(required_version) and (required_addon not in ignore):
                report.add(Record(PROBLEM, "Version mismatch for addon %s. Required: %s, Available: %s "
                                  % (required_addon, required_version, available_version)))


def _get_ignore_list(branch_name):

    if branch_name == "leia":
        common_ignore_deps.extend(["inputstream.adaptive", "inputstream.rtmp",
                                   "script.module.pycryptodome"])
        return common_ignore_deps

    elif branch_name == "krypton":
        common_ignore_deps.extend(["inputstream.adaptive", "inputstream.rtmp"])
        return common_ignore_deps

    else:
        return common_ignore_deps


def _get_users_dependencies(parsed_xml):
    """Gets all the dependencies from a given addon
        :parsed_xml: parsed addon.xml
    """

    return {
        i.get("addon"): i.get("version")
        for i in parsed_xml.findall("requires/import")
    }
