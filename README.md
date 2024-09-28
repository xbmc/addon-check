[![Build and test addon-checker](https://github.com/xbmc/addon-check/actions/workflows/test_and_lint_matrix.yml/badge.svg)](https://github.com/xbmc/addon-check/actions/workflows/test_and_lint_matrix.yml)
[![PyPI version](https://badge.fury.io/py/kodi-addon-checker.svg)](https://badge.fury.io/py/kodi-addon-checker)

# Kodi Addon checker

This tool checks the Kodi repo for best practices and produces a report containing found problems and warnings.

It can also be used locally for detecting problems in your addons.

## Features

- Checks if artwork is available and if the size is as [defined](https://kodi.wiki/view/Add-on_structure#icon.png)

- Checks if all artworks(images/fanart/screenshot) are valid.

- Checks if addon.xml and license file exists for an addon.

- Checks if the version in addon.xml is valid (for repository generator)

- Checks if all xml files are valid.

- Check if all the json files are valid.

- Checks if the addon id in addon.xml matches with the folder name.

- Checks if the addon uses the old strings.xml translation format.

- Check if the addon uses the old language folders (English vs resource.language.en_gb).

- Checks for various blacklisted strings.

- Check for blacklisted filetypes.

- Check for new dependencies present in addon.xml files.

- Check the complexity of the entrypoint files for addon.

- Check if addon already exists in any of lower repositories

- Check if addon already exists in any of the upper repositories (with non-compatible python abi) with a lower version, thus preventing a user kodi migration

- Check if addon is compatible with python3 or not

- Check specific [version attribute](https://kodi.wiki/view/Addon.xml#version_attribute_2)

- Validate addon.xml against schemas

- Check if files in addon are marked as executable or not.

- Check for unused script.module addons

- Check presence of extensions in addon dependencies.

- Check for valid forum, source and website value in addon.xml

- Check if all PO files are valid

All of the validation and checks are done according to the kodi [addon rules](https://kodi.wiki/view/Add-on_rules)

## Installation


* You will need Python3.

Then you can directly install it from pip package:

```bash
pip install kodi-addon-checker
```

#### For Development

* Clone the repository
```
git clone https://github.com/xbmc/addon-check
```

* `cd <path-to-cloned-repo>`
* Install the requirements:
```
pip install -r requirements.txt
```

## Usage

* If you are in add-on directory:
    - Execute `kodi-addon-checker`

* If you want to run it from any other directory
    - Execute
    ```
    kodi-addon-checker <path-to-addon>
    ```

You can use the tool with the following options:
```

--version                   version of the tool
--branch                    name of the branch the tool is to run on
--PR                        only when the tool is running on a pull request
--allow-folder-id-mismatch  allow the addon's folder name and id to mismatch
--reporter                  enable a reporter, this option can be used multiple times
--enable-debug-log          enable debug logging to kodi-addon-checker.log
--skip-dependency-checks    do not check if addon dependencies are available in the official Kodi addon repository
```
