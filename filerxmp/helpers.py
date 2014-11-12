# -*- coding: utf-8 -*-
from __future__ import absolute_import
import iptcinfo
from PIL import Image as PILImage
from dateutil import parser
from pytz import timezone


def get_xmp_string_from__file(path):
    """This function parses given files for xmp metadata.

    :param path: file path to parse
    :rtype: False or XML string
    """
    try:
        fs = open(path)
        img_raw = fs.read()
        fs.close()

        xmp_start = img_raw.find('<x:xmpmeta')
        xmp_end = img_raw.find('</x:xmpmeta>')
        xmp_str = img_raw[xmp_start:xmp_end + 12]

    except IOError:
        return False

    if xmp_start < 0:
        return False
    else:
        return xmp_str


def get_iptc_keywords(path):
    """Returns iptc keywords or empty list for file at ``path``."""
    im = PILImage.open(path)
    im.verify()

    if im.format == 'JPEG':
        iptc = iptcinfo.IPTCInfo(path)
        if len(iptc.keywords) > 0:
            return iptc.keywords[0].split(',')

    return []



def get_datetime_or_none(timestring):
    """This function takes a string and tries to return a valid datetime.

    :param timestring: string with valid definition of a datetime
    :rtype: datetime object or None
    """
    if len(timestring) < 1:
        return None

    try:
        result = parser.parse(timestring)
        if not result.tzinfo:
            tz = timezone('Europe/Vienna')
            result = tz.localize(result)
        return result
    except ValueError:
        return None

