import pathlib
import re
import os
from .report import Report
from .common import relative_path
from .record import PROBLEM, Record


def find_file(name: str, path: str):
    """Looks for a file in a given path.
        :name: name of the file to look for
        :path: path of the directory.
        :return: full path for the file.
    """
    for file_name in os.listdir(path):
        match = re.match(name, file_name, re.IGNORECASE)
        if match is not None:
            return os.path.join(path, match.string)
    return


def find_files_recursive(name: str, path: str):
    """This looks for a file but only returns the first occurance
        :name: name of the file to look for
        :path: path of directory to look for the file
    """
    for root, _, files in os.walk(path):
        for file in files:
            if name in file:
                yield os.path.join(root, file)


def create_file_index(path: str):
    """Creates a list having multiple dictionaries in following format:
        [{'name':<file_name>, 'path': '<path_to_file>'}]

        :path: path for the directory
    """
    file_index = []
    for dirs in os.walk(path):
        if dirs[0][0] != '.':
            for file_name in dirs[2]:
                if file_name[0] != '.':
                    file_index.append({"path": dirs[0], "name": file_name})
    return file_index


def find_in_file(path: str, search_terms: list, whitelisted_file_types: list):
    """Finds for particular terms in whitelisted file type i.e .py or .xml
        :path: path of a directory
        :search_term: list of all the terms to be searched
        :whitelisted_file_type: list of all the whitelisted file types
    """
    results = []
    if len(search_terms) > 0:
        for directory in os.walk(path):
            for file_name in directory[2]:
                if pathlib.Path(file_name).suffix in whitelisted_file_types or len(whitelisted_file_types) == 0:
                    file_path = os.path.join(directory[0], file_name)

                    searchfile = open(file_path, "r", encoding="utf8")
                    linenumber = 0
                    for line in searchfile:
                        linenumber = linenumber + 1
                        for term in search_terms:
                            if term in line:
                                results.append({"term": term, "line": line.strip(
                                ), "searchfile": file_path, "linenumber": linenumber})
                    searchfile.close()
    return results


def addon_file_exists(report: Report, addon_path: str, file_name: str):
    """check whether addon file exists or not
        :addon_path: path to the addon
        :file_name: name of the addon file
    """
    if find_file(file_name, addon_path) is None:
        report.add(Record(PROBLEM, "Not found %s in folder %s" % (file_name, relative_path(addon_path))))
