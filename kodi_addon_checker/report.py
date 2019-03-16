"""
    Copyright (C) 2017-2018 Team Kodi
    This file is part of Kodi - kodi.tv

    SPDX-License-Identifier: GPL-3.0-only
    See LICENSES/README.md for more information.
"""

from .record import PROBLEM, WARNING, Record
from .reporter import ReportManager


class Report():
    def __init__(self, artifact_name):
        """
        Create a new report for the given artifact. The artifact can be a repo, add-on or file.
        :param artifact_name: the artifact name
        """
        self.artifact_name = artifact_name
        self.problem_count = 0
        self.warning_count = 0
        self.information_count = 0

    def add(self, report):
        """
        Add a sub record/report to this report.
        :param report: a record or report
        :return: None
        """
        if isinstance(report, Record):
            for reporter in ReportManager.getEnabledReporters():
                reporter.report(report)
            if PROBLEM == report.log_level:
                self.problem_count += 1
            elif WARNING == report.log_level:
                self.warning_count += 1
            else:
                self.information_count += 1
        else:
            self.problem_count += report.problem_count
            self.warning_count += report.warning_count
            self.information_count += report.information_count
