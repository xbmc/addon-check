import os
import setuptools

import kodi_addon_checker


with open('requirements.txt') as f:
    requirements = f.read().splitlines()

_ROOT = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(_ROOT, 'README.md')) as f:
    LONG_DESCRIPTION = f.read()

setuptools.setup(
    name="kodi-addon-checker",
    version=kodi_addon_checker.__version__,
    description="Check kodi addons or whole kodi repositories for errors and best practices.",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author="Team Kodi",
    url="https://github.com/xbmc/addon-check",
    download_url="https://github.com/xbmc/addon-check/archive/master.zip",
    packages=setuptools.find_packages(exclude=['script.test', 'tests*']),
    package_data={'kodi_addon_checker': ['xml_schema/*.xsd']},
    install_requires=requirements,
    python_requires=">=3.5",
    setup_requires=['setuptools>=38.6.0'],
    entry_points={'console_scripts': [
        'kodi-addon-checker = kodi_addon_checker.__main__:main']},
    keywords='kodi add-on add-on_checker',
    classifiers=[
        "Operating System :: POSIX :: Linux",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Topic :: Utilities"
    ] + [('Programming Language :: Python :: %s' % x) for x in '3 3.5 3.6 3.7'.split()]
)
