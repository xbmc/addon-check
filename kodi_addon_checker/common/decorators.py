"""
    Copyright (C) 2017-2018 Team Kodi
    This file is part of Kodi - kodi.tv

    SPDX-License-Identifier: GPL-3.0-only
    See LICENSES/README.md for more information.
"""

import os


class posix_only():
    def __init__(self, f):
        self.f = f

    def __call__(self, *args, **kwargs):
        if os.name == "nt":
            return

        self.f(*args, **kwargs)
