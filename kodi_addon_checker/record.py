"""
    Copyright (C) 2018-201 Team Kodi
    This file is part of Kodi - kodi.tv

    SPDX-License-Identifier: GPL-3.0-only
    See LICENSES/README.md for more information.
"""

PROBLEM = "ERROR"
WARNING = "WARN"
INFORMATION = "INFO"


class Record():
    def __init__(self, log_level, message):
        """
        Create a record which is the low level entry in Report to represent logs.
        :param log_level: "ERROR", "WARN" or "INFO"
        :param message: the actual log message
        """
        self.log_level = log_level
        self.message = message

    def add(self, record):
        pass

    def __str__(self):
        """
        Text representation of record.
        :return: text representation of report
        """
        return f"{self.log_level}: {self.message}"
