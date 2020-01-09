# -*- coding: utf-8 -*-

"""
Luci is a web-based high availability administration application built
on the TurboGears 2 framework.
"""

__all__ = [
    'authors',
    'fancy_name',
    'description',
    'licence',
    'version',
    'author',
    'email',
    'version_info',
    'config_template',
]


authors = """\
Ryan McCabe <rmccabe@redhat.com>
Chris Feist <cfeist@redhat.com>
Jan Pokorný
Eve McGlynn
Jeremy Perry
"""

__version__ = '0.26.0'
__licence__ = 'GPLv2'
__author__ = ", ".join(
    [a.partition(' <')[0] for a in authors.strip().split('\n')]
)

# "fancy name" is used to form .egg-info directory etc., not a strict name
fancy_name = __name__
description = __doc__
version = __version__
licence = __licence__
author = __author__
email = ", ".join(
    filter(
        lambda e: e != "",
        [a.partition(' <')[2].rstrip('>') for a in authors.strip().split('\n')]
    )
)
version_info = tuple([int(n) for n in __version__.split('.')])

# This is common for setup.py and luci.initwrappers
config_template = 'config/config.tmpl'
