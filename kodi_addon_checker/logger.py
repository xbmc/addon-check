"""
    Copyright (C) 2017-2018 Team Kodi
    This file is part of Kodi - kodi.tv

    SPDX-License-Identifier: GPL-3.0-only
    See LICENSES/README.md for more information.
"""

import logging
import logging.handlers


class Logger:

    @staticmethod
    def create_logger(debug_filename, logger_name, enabled=False):
        """Creates a logger format for error logging
        :debug_filename: path and filename of the debug log
        :logger_name: name of the logger to create
        :enabled: enable to write the log to provided filename, otherwise uses a NullHandler
        """
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
        formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s:%(name)s:%(funcName)s: %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')

        if enabled:
            # DEBUG log to 'kodi-addon-checker.log'
            debug_log_handler = logging.handlers.RotatingFileHandler(debug_filename, encoding='utf-8', mode="w")
            debug_log_handler.setLevel(logging.DEBUG)
            debug_log_handler.setFormatter(formatter)
            logger.addHandler(debug_log_handler)
        else:
            logger.addHandler(logging.NullHandler())

        return logger
