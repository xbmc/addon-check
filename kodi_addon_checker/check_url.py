"""
    Copyright (C) 2017-2018 Team Kodi
    This file is part of Kodi - kodi.tv

    SPDX-License-Identifier: GPL-3.0-only
    See LICENSES/README.md for more information.
"""

import requests
import urllib3

from .record import WARNING, Record
from .report import Report


def check_url(report: Report, parsed_xml):
    """
     Checks for valid forum, source and website urls
        :parsed_xml: parsed addon.xml file
    """

    # ElementTree doesn't support the following or syntax
    # ./extension[@point='kodi.addon.metadata' or @point='xbmc.addon.metadata']/(forum|source|website)
    sources = parsed_xml.findall("./extension[@point='kodi.addon.metadata']/forum")
    sources += parsed_xml.findall("./extension[@point='xbmc.addon.metadata']/forum")

    sources += parsed_xml.findall("./extension[@point='kodi.addon.metadata']/source")
    sources += parsed_xml.findall("./extension[@point='xbmc.addon.metadata']/source")

    sources += parsed_xml.findall("./extension[@point='kodi.addon.metadata']/website")
    sources += parsed_xml.findall("./extension[@point='xbmc.addon.metadata']/website")

    for source in sources:
        if not source.text:
            continue

        url = source.text
        scheme = True

        try:
            if urllib3.util.parse_url(source.text).scheme is None:
                url = f"http://{source.text}"
                scheme = False

            r = requests.head(url, allow_redirects=True, timeout=5)
            host = urllib3.util.parse_url(r.url).host
            if not scheme and not host.endswith(source.text):
                report.add(Record(WARNING, f"{source.text} redirects to {host}"))
            elif scheme and r.url.rstrip('/') != url.rstrip('/'):
                report.add(Record(WARNING, f"{source.text} redirects to {r.url}"))
            r.raise_for_status()
        except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout, requests.exceptions.HTTPError,
                requests.exceptions.InvalidSchema, requests.exceptions.MissingSchema, requests.exceptions.ReadTimeout,
                requests.exceptions.SSLError, urllib3.exceptions.LocationParseError) as e:
            report.add(Record(WARNING, e))
