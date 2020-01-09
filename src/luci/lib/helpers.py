# Copyright (C) 2009-2010 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

# -*- coding: utf-8 -*-
"""Helpers used in Luci."""

__all__ = ['singleton',
           'relativeUrlSlashPrefix', 'relativeUrlList2Str']

from pylons.i18n import ugettext, lazy_ugettext

def singleton(cls):
    """Trivial class decorator that replace the class with an instance of it."""
    return cls()


#-------------------------------------------------------------------------------
# Functions related to URL.

def relativeUrlSlashPrefix(url_string):
    """Ensures that given URL (as a string) starts with a slash.

    Keyword arguments:
        url_string    URL (as a string).

    Return value(s):
        'url_string' argument surely starting with a slash.

    """
    if not url_string.startswith(u'/'):
        url_string = u'/' + url_string
    return url_string


def relativeUrlList2Str(*url_parts):
    """Converts list of URL parts to string beginning with '/'.

    Keyword arguments:
        url_parts    List of URL parts.

    Return value(s):
        All URL parts joined with a slash, the whole such string starts also
        with a slash.

    """
    return relativeUrlSlashPrefix(u'/'.join(url_parts))
