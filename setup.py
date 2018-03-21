import os
import setuptools


REQUIRES = [
    'Pillow',
    'requests'
]

_ROOT = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(_ROOT, 'README.md')) as f:
    LONG_DESCRIPTION = '\n' + f.read()

setuptools.setup(
    name="kodi-addon-checker",
    version="0.0.1",
    description="Automatic checks for new repository submissions.",
    long_description=LONG_DESCRIPTION,
    author="Team Kodi",
    url="https://github.com/xbmc/addon-check",
    download_url="https://github.com/xbmc/addon-check/archive/master.zip",
    packages=setuptools.find_packages(),
    install_requires=REQUIRES,
    entry_points={'console_scripts': ['kodi-addon-checker = kodi_addon_checker.__main__:main']},
    keywords='kodi add-on add-on_checker',
    classifiers=[
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Topic :: Utilities"
    ] + [('Programming Language :: Python :: %s' % x) for x in '3 3.4 3.5 3.6'.split()]
)
