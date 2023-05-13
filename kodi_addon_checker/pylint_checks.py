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
from .record import Record, WARNING

# TODO: Do not repeat name of same file in report just do something like . utils.py - 90,1780 ?
table_format = [["File path", "Line no", "Message", "message-id"]]


def short_path(path):
    return os.path.split(path)[1]


def analyze(report: Report, filename: str):

    ARGS = ["-r", "n", "--score=yes", "--lint-all=y", "--rcfile=kodi_addon_checker/.pylintrc"]
    out = io.StringIO()
    Run([filename] + ARGS, reporter=JSONReporter(out), do_exit=False)

    json_data = json.loads(out.getvalue())
    for issue in json_data:
        table_format.append([short_path(issue['path']), issue['line'], issue['message'], issue['message-id']])

    table = AsciiTable(table_format).table
    report.add(Record(WARNING, table))
