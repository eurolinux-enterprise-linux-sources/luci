# Copyright (C) 2010 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

"""\
Wrappers for parts used during initial phase of running luci.
"""

from pylons.util import PylonsInstaller as _PylonsInstaller
from repoze.who.config import WhoConfig as _WhoConfig, make_middleware_with_config

from luci import config_template


class PylonsInstaller(_PylonsInstaller):
    config_file = config_template


# Unfortunately, original WhoConfig doesn't strip values obtained from
# [DEFAULT] section of configuration file (and repoze.who plugins' factories
# are not prepared for these values) so this will patch ``text'' argument
# to ``parse'' method so that it contains only necessary sections from
# the whole configuration file (i.e. also excluding [DEFAULT] section)
def repoze_who_make_middleware_with_config(app,
                                           global_conf,
                                           config_file,
                                           log_file=None,
                                           log_level=None,
                                           safe_config=True):

    class WhoConfig(_WhoConfig):
        def parse(self, text):
            from ConfigParser import ConfigParser, SafeConfigParser, NoSectionError
            from StringIO import StringIO

            in_parser = ConfigParser(
                            defaults=global_conf
                        )
            in_parser.readfp(text)
            text = StringIO()
            out_parser = SafeConfigParser()
            sections = filter(
                           lambda s:
                               s in ('general', 'identifiers', 'authenticators',
                                    'challengers', 'mdproviders')
                               or s.startswith('plugin:'),
                           in_parser.sections()
                       )
            for section in sections:
                for option in filter(lambda o: o not in in_parser.defaults(),
                                     in_parser.options(section)):
                    try:
                        out_parser.set(section, option, in_parser.get(section, option))
                    except NoSectionError:
                        out_parser.add_section(section)
                        out_parser.set(section, option, in_parser.get(section, option))
            out_parser.write(text)
            # This is necessary
            text.seek(0)
            _WhoConfig.parse(self, text)

    if not safe_config:
        make_middleware_with_config.func_globals["WhoConfig"] = WhoConfig

    app = make_middleware_with_config(
        app,
        global_conf,
        config_file,
        log_file=None,
        log_level=None,
    )

    return app


# This is a workaround for problem, that repoze.who < 1.0.14 cannot handle
# "timeout" and "reissue_time" (+ "userid_checker") parameters when passed
# into make_plugin function of repoze.who.plugins.auth_tkt.
#
# The only remaining problem is that the session will not timeout after some
# time of inactivity in case of repoze.who < 1.0.14.
def auth_tkt_make_plugin(secret=None,
                         secretfile=None,
                         cookie_name='auth_tkt',
                         secure=False,
                         include_ip=False,
                         timeout=None,
                         reissue_time=None,
                         userid_checker=None):
    # We can presume that this package and function exist (see setup.py).
    from repoze.who.plugins.auth_tkt import make_plugin
    try:
        return make_plugin(secret=secret,
                           secretfile=secretfile,
                           cookie_name=cookie_name,
                           secure=secure,
                           include_ip=include_ip,
                           timeout=timeout,
                           reissue_time=reissue_time,
                           userid_checker=userid_checker)
    except TypeError:
        # Workaround for repoze.who < 1.0.14 case.
        return make_plugin(secret=secret,
                           secretfile=secretfile,
                           cookie_name=cookie_name,
                           secure=secure,
                           include_ip=include_ip)
