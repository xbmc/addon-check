"""
    Copyright (C) 2017-2018 Team Kodi
    This file is part of Kodi - kodi.tv

    SPDX-License-Identifier: GPL-3.0-only
    See LICENSES/README.md for more information.
"""

from kodi_addon_checker.record import INFORMATION, PROBLEM, WARNING
from kodi_addon_checker.report import Record
from kodi_addon_checker.reporter import Reporter, reporter


def colorPrint(string, color):
    """
    Utility function to print message to console.
    :param string: the message to print
    :param color: message color
    :return:
    """
    print(f"\033[{color}m{string}\033[0m")


@reporter(name="console", enabled=True)
class ConsoleReporter(Reporter):
    """Present Report on the console
    """
    def report(self, report):
        if isinstance(report, Record):
            if report.log_level == INFORMATION:
                colorPrint(report, "34")
            elif report.log_level == WARNING:
                colorPrint(report, "35")
            elif report.log_level == PROBLEM:
                colorPrint(report, "31")
        else:
            for rep in report:
                self.report(rep)
