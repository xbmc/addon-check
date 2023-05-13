"""
    Copyright (C) 2019 Team Kodi
    This file is part of Kodi - kodi.tv

    SPDX-License-Identifier: GPL-3.0-only
    See LICENSES/README.md for more information.
"""

import io
import json
import os

from pylint.lint import Run
from pylint.reporters.json import JSONReporter
from terminaltables import AsciiTable

from .report import Report
from .record import Record, WARNING, INFORMATION


def analyze(report: Report, filename: str):
    table_format = [["Line no", "Message", "message-id"]]

    ARGS = ["-r", "n", "--score=yes", "--lint-all=y",
            "--rcfile={}/.pylintrc".format(os.path.dirname(os.path.realpath(__file__)))]

    out = io.StringIO()
    Run([filename] + ARGS, reporter=JSONReporter(out), do_exit=False)

    if out.getvalue():
        json_data = json.loads(out.getvalue())
        paths = []

        for dicts in json_data:
            paths.append(dicts['path'])

        paths = list(set(paths))
        data_dict = _path_dictionary(json_data, paths)

        for path in paths:
            report.add(Record(INFORMATION, (path + '\n')))
            for issue in data_dict[path]:
                table_format.append([issue['line'], issue['message'], issue['message-id'], ''])
            table = AsciiTable(table_format).table
            report.add(Record(WARNING, table))
            table_format = [["Line no", "Message", "message-id"]]
    else:
        report.add(Record(INFORMATION, "Addin is free from pylint errors"))


def short_path(path):
    return os.path.split(path)[1]


def _path_dictionary(data, paths):
    path_dict = {}

    for issue in data:
        if issue['path'] not in paths:
            continue
        elif issue['path'] not in path_dict:
            path_dict[issue['path']] = [issue]
        else:
            path_dict[issue['path']].append(issue)

    return path_dict
