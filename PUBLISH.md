# Publish
Make sure to run this with python 3.
Increase the version flag in `kodi_addon_checker/__init__.py`

## Run these commands
```py
py setup.py sdist bdist_wheel
twine upload dist/*
```
