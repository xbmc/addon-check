"""
    Copyright (C) 2017-2018 Team Kodi
    This file is part of Kodi - kodi.tv

    SPDX-License-Identifier: GPL-3.0-only
    See LICENSES/README.md for more information.
"""

__all__ = ["decorators", "has_transparency", "relative_path", "load_plugins"]

import importlib
import os
import pkgutil
import sys

REL_PATH = ""


def has_transparency(im):
    """Check the transparency(aplha layer) in the given image

        :im: PIL.Image object
    """
    try:
        if im.mode == "RGBA":
            alpha = im.split()[-1]
            listdata = list(alpha.getdata())
            first_transparent_pixel = next(x[0]
                                           for x in enumerate(listdata) if x[1] < 255)
            if first_transparent_pixel is not None:
                return True
        return False
    except StopIteration:
        return False


def load_plugins():
    """Load the reporter plugins
    """
    plugins_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "plugins")
    sys.path.append(plugins_dir)
    for _, package_name, _ in pkgutil.iter_modules([plugins_dir]):
        if "test_" not in package_name:
            importlib.import_module(package_name)


def relative_path(file_path):
    """Return the relative_path of the file
    """
    path_to_print = file_path[len(REL_PATH):]
    return ".{}".format(path_to_print)
