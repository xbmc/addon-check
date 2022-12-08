"""
    Copyright (C) 2017-2018 Team Kodi
    This file is part of Kodi - kodi.tv

    SPDX-License-Identifier: GPL-3.0-only
    See LICENSES/README.md for more information.
"""

import json
import os
from argparse import ArgumentParser

from kodi_addon_checker.reporter import ReportManager


class Config():
    def __init__(self, repo_path, cmd_args=None):
        """
        Create Config object using .tests-config.json and command line arguments.
        :param repo_path: the repo path which contains .tests-config.json.
        :param cmd_args: argparse object
        """
        self.configs = {} if cmd_args is None else vars(cmd_args)
        self._load_config(repo_path)

    def _load_config(self, repo_path):
        if repo_path is None:
            return
        config_path = os.path.join(repo_path, '.tests-config.json')
        if os.path.isfile(config_path):
            with open(config_path, "r", encoding="utf8") as json_data:
                file_config = json.load(json_data)
                if file_config is not None:
                    for key, value in self.configs.items():
                        if value is not None:
                            file_config[key] = value
                    self.configs = file_config

    def is_enabled(self, value):
        return self.configs.get(value, False)

    def __getitem__(self, item):
        return self.configs.get(item)


class ConfigManager():
    configurations = {}

    @classmethod
    def register(cls, config, description, default_value, action):
        cls.configurations[config] = [description, default_value, action]

    @classmethod
    def fill_cmd_args(cls, parser: ArgumentParser):
        # Add --reporter
        parser.add_argument("--reporter", action="append", choices=list(ReportManager.reporters.keys()),
                            help="""enable a reporter with the given name.
                            You can use this option multiple times to enable more than one reporters""")

    @classmethod
    def process_config(cls, config):
        reporters = config["reporter"]
        if reporters is not None:
            # To disable all, pass empty array in .tests-config.json
            ReportManager.enable(reporters)
