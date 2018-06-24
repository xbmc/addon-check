from distutils.version import LooseVersion
from .report import Report
from .record import PROBLEM, Record, WARNING


def check_addon_dependencies(report: Report, repo_addons: dict, parsed_xml):
    """Check for any new dependencies in addon.xml file and reports them
        :parsed_xml: parsed addon.xml file
        :repo_addons: dictionary having all the addon list of a particular
                        version of kodi
    """

    deps = _get_users_dependencies(parsed_xml)
    ignore = ['xbmc.metadata.scraper.albums', 'xbmc.metadata.scraper.albums', 'xbmc.metadata.scraper.movies',
              'xbmc.metadata.scraper.musicvideos', 'xbmc.metadata.scraper.tvshows', 'xbmc.metadata.scraper.library',
              'xbmc.ui.screensaver', 'xbmc.player.musicviz', 'xbmc.python.pluginsource', 'xbmc.python.script',
              'xbmc.python.weather', 'xbmc.python.lyrics', 'xbmc.python.library', 'xbmc.python.module',
              'xbmc.subtitle.module', 'kodi.context.item', 'kodi.game.controller', 'xbmc.gui.skin',
              'xbmc.webinterface', 'xbmc.addon.repository', 'xbmc.pvrclient', 'kodi.gameclient',
              'kodi.peripheral', 'xbmc.addon.video', 'xbmc.addon.audio', 'xbmc.addon.image',
              'xbmc.addon.executable', 'kodi.addon.game', 'kodi.audioencoder', 'kodi.audiodecoder',
              'xbmc.service', 'kodi.resource.images', 'kodi.resource.language', 'kodi.resource.uisounds',
              'kodi.resource.games', 'kodi.resource.font', 'kodi.inputstream', 'kodi.vfs', 'kodi.imagedecoder',
              'xbmc.json', 'xbmc.gui', 'xbmc.json', 'xbmc.metadata', 'xbmc.python', 'script.module.pil',
              'inputstream.adaptive', 'script.module.pycryptodome']

    for required_addon, required_version in deps.items():
        if required_addon not in repo_addons:
            if required_addon not in ignore:
                report.add(Record(
                    PROBLEM, "Required addon %s not available in current repository." % required_addon))
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


def _get_users_dependencies(parsed_xml):
    """Gets all the dependencies from a given addon
        :parsed_xml: parsed addon.xml
    """

    return {
        i.get("addon"): i.get("version")
        for i in parsed_xml.findall("requires/import")
    }
