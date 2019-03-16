"""
    Copyright (C) 2017-2018 Team Kodi
    This file is part of Kodi - kodi.tv

    SPDX-License-Identifier: GPL-3.0-only
    See LICENSES/README.md for more information.
"""

from kodi_addon_checker.report import Record
from kodi_addon_checker.reporter import Reporter, reporter


@reporter(name="array", enabled=False)
class ArrayReporter(Reporter):
    def __init__(self):
        self.reports = []

    def report(self, report):
        if isinstance(report, Record):
            self.reports.append(report)
