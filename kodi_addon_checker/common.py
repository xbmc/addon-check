import importlib
import os
import pkgutil
import sys


def has_transparency(im):
    try:
        if im.mode == "RGBA":
            alpha = im.split()[-1]
            listdata = list(alpha.getdata())
            first_transparent_pixel = next(x[0]
                                           for x in enumerate(listdata) if x[1] < 255)
            if first_transparent_pixel is not None:
                return True
        else:
            return False
    except StopIteration:
        return False


def load_plugins():
    plugins_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "plugins")
    sys.path.append(plugins_dir)
    for importer, package_name, _ in pkgutil.iter_modules([plugins_dir]):
        if "test_" not in package_name:
            importlib.import_module(package_name)
