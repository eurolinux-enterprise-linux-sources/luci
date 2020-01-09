# -*- coding: utf-8 -*-
"""WSGI middleware initialization for the luci application."""

from luci.config.app_cfg import base_config
from luci.config.environment import load_environment
from luci.initwrappers import repoze_who_make_middleware_with_config


__all__ = ['make_app']

# Use base_config to setup the necessary PasteDeploy application factory.
# make_base_app will wrap the TG2 app with all the middleware it needs.
make_base_app = base_config.setup_tg_wsgi_app(load_environment)


def make_app(global_conf, full_stack=True, **app_conf):
    """
    Set luci up with the settings found in the PasteDeploy configuration
    file used.

    :param global_conf: The global settings for luci (those
        defined under the ``[DEFAULT]`` section).
    :type global_conf: dict
    :param full_stack: Should the whole TG2 stack be set up?
    :type full_stack: str or bool
    :return: The luci application with all the relevant middleware
        loaded.

    This is the PasteDeploy factory for the luci application.

    ``app_conf`` contains all the application-specific settings (those defined
    under ``[app:main]``.


    """
    app = make_base_app(global_conf, full_stack=True, **app_conf)


    # Add repoze.who middleware

    who_config_file = 'who.ini'
    who_log_file = 'stdout'
    who_log_level = 'warning'
    who_conf = global_conf.copy()

    for who_opt in filter(lambda i: i.startswith("who."), app_conf.iterkeys()):
        if who_opt == "who.config_file":
            who_config_file = app_conf.get(who_opt)
        elif who_opt == "who.log_file":
            who_log_file = app_conf.get(who_opt)
        elif who_opt == "who.log_level":
            who_log_level = app_conf.get(who_opt)
        else:
            who_conf[who_opt] = app_conf.get(who_opt)

    app = repoze_who_make_middleware_with_config(
              app,
              who_conf,
              who_config_file,
              who_log_file,
              who_log_level,
              safe_config = False
          )


    return app
