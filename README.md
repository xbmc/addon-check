[![Build Status](https://travis-ci.org/xbmc/addon-check.svg?branch=master)](https://travis-ci.org/xbmc/addon-check)

# Kodi Addon checker

This tool checks the Kodi repo for best practices and creates problem and warning reports

## Features
- Checks if all images are valid images

- Checks if all xml files are valid

- Checks if addon.xml and license file exists for an addon

- Checks if the addon id in addon.xml matches with the folder name

- Checks if artwork is available and if the size is as defined

- Checks if the addon uses the old strings.xml translation format

- Check if the addon uses the old language folders (English vs resource.language.en_gb)

- Checks for various blacklisted strings

- Check for blacklisted filetypes

## Installation

Open Terminal in addon-check folder and execute the following command

### Unix
```
sudo -H python setup.py install
```
## Windows
```
py setup.py install
```

## How to use

1. Open Terminal in addon-repo

2. Execute kodi-addon-checker

### Unix
```
kodi-addon-checker
```

### Windows
```
py -m kodi_addon_checker
```

Above command will run kodi-addon-checker in current working directory

## Uninstall
### Unix
```
pip unistall kodi-addon-checker
```

### Windows
```
py -m pip uninstall kodi-addon-checker
```