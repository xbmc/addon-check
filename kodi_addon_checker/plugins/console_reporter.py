"""
    Copyright (C) 2017-2018 Team Kodi
    This file is part of Kodi - kodi.tv

    SPDX-License-Identifier: GPL-3.0-only
    See LICENSES/README.md for more information.
"""

from kodi_addon_checker.record import INFORMATION, PROBLEM, WARNING
from kodi_addon_checker.report import Record
from kodi_addon_checker.reporter import Reporter, reporter


def color_print(string, color):
    """
    Utility function to print message to console.
    :param string: the message to print
    :param color: message color
    :return:
    """
    print("\033[%sm%s\033[0m" % (color, string))


@reporter(name="console", enabled=True)
class ConsoleReporter(Reporter):
    """Present Report on the console
    """
    def report(self, report):
        if isinstance(report, Record):
            if report.log_level == INFORMATION:
                color_print(report, "34")
            elif report.log_level == WARNING:
                color_print(report, "35")
            elif report.log_level == PROBLEM:
                color_print(report, "31")
        else:
            for rep in report:
                self.report(rep)
