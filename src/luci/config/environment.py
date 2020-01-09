# -*- coding: utf-8 -*-
"""WSGI environment setup for luci."""

from luci.config.app_cfg import base_config

__all__ = ['load_environment']


# This will enable removing some values from ``global_conf'' that had a use
# only for parsing + string interpolation of certain sections in config file;
# also values prefixed with "who." in ``app_conf'' are no longer needed
def make_load_environment(wrapped_f):

    def load_environment(global_conf, app_conf):
        del_global = filter(
                         lambda o: o.startswith("tmp.")
                                   or o.startswith("def."),
                         global_conf.iterkeys()
        )
        for opt in del_global:
            global_conf.pop(opt)

        del_app = filter(
                      lambda o: o.startswith("who."),
                      app_conf.iterkeys()
        )
        for opt in del_app:
            app_conf.pop(opt)

        wrapped_f(global_conf, app_conf)

    # def load_environment

    return load_environment


load_environment = make_load_environment(base_config.make_load_environment())
