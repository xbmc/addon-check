from kodi_addon_checker.report import Report
from kodi_addon_checker.common import relative_path
from kodi_addon_checker import handle_files
from kodi_addon_checker.record import PROBLEM, Record, WARNING


def check_for_legacy_strings_xml(report: Report, addon_path: str):
    """Find for the string.xml file in addon which was used in old versions
        :addon_path: path of the addon
    """
    if handle_files.find_file_recursive("strings.xml", addon_path) is not None:
        report.add(
            Record(PROBLEM, "Found strings.xml in folder %s please migrate to strings.po." % relative_path(addon_path)))


def find_blacklisted_strings(report: Report, addon_path: str, problems: list, warnings: list, file_types: list):
    """Find for any blacklisted strings in the addons files
        :addon_path: Path of theh addon
        :problems: List of all the strings that will cause problem being in an addon
        :warnings: List of all the strings that shouldn't be in addon
                        but doesn't cause any problem
        :file_type: List of the whitelisted files to look into
    """
    for result in handle_files.find_in_file(addon_path, problems, file_types):
        report.add(Record(PROBLEM, "Found blacklisted term %s in file %s:%s (%s)"
                          % (result["term"], result["searchfile"], result["linenumber"], result["line"])))

    for result in handle_files.find_in_file(addon_path, warnings, file_types):
        report.add(Record(WARNING, "Found blacklisted term %s in file %s:%s (%s)"
                          % (result["term"], result["searchfile"], result["linenumber"], result["line"])))
