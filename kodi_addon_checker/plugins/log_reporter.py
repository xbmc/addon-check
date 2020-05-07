"""
    Copyright (C) 2017-2018 Team Kodi
    This file is part of Kodi - kodi.tv

    SPDX-License-Identifier: GPL-3.0-only
    See LICENSES/README.md for more information.
"""
import logging
import logging.handlers

from kodi_addon_checker.common import get_reporter_log_path
from kodi_addon_checker.report import Record
from kodi_addon_checker.reporter import Reporter, reporter


@reporter(name="log", enabled=False)
class LogReporter(Reporter):

    def __init__(self):
        self.logger = None
        self.log_file_path = get_reporter_log_path()

    def create_logger(self):
        logger = logging.getLogger("log_reporter")
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
        formatter = logging.Formatter(fmt="%(asctime)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        log_handler = logging.handlers.RotatingFileHandler(self.log_file_path, encoding="utf-8", mode="w")
        log_handler.setFormatter(formatter)
        log_handler.setLevel(logging.DEBUG)
        logger.addHandler(log_handler)
        self.logger = logger

    def report(self, report):
        if not self.logger:
            self.create_logger()

        if isinstance(report, Record):
            self.logger.info(report)
        else:
            for rep in report:
                self.report(rep)
