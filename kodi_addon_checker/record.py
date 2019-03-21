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
    def __init__(self, log_level, message, start_line=-1, end_line=-1, start_char_position=-1,
                 end_char_position=-1):
        """
        Create a record which is the low level entry in Report to represent logs.
        :param log_level: "ERROR", "WARN" or "INFO"
        :param message: the actual log message
        :param start_line: for text files, provide the start line of issue
        :param end_line: for text files, provide the end line of issue
        :param start_char_position: for text files, provide the start character position of issue in start line
        :param end_char_position: for text files, provide the end character position of issue in end line
        """
        self.log_level = log_level
        self.message = message
        self.start_line = start_line
        self.end_line = end_line
        self.start_char_position = start_char_position
        self.end_char_position = end_char_position

    def add(self, record):
        pass

    def __str__(self):
        """
        Text representation of record.
        :return: text representation of report
        """
        if self.start_line == -1:
            return "%s: %s" % (self.log_level, self.message)

        if self.start_char_position == -1:
            return "%s [%d-%d]: %s" % (self.log_level, self.start_line, self.end_line, self.message)

        return "%s [%d:%d-%d:%d]: %s" % (
            self.log_level, self.start_line, self.start_char_position, self.end_line, self.end_char_position,
            self.message)
