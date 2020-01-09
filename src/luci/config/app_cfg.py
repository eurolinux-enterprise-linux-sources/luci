# -*- coding: utf-8 -*-
"""
Global configuration file for TG2-specific settings in luci.

Please note that **all the argument values are strings**. If you want to
convert them into boolean, for example, you should use the
:func:`paste.deploy.converters.asbool` function, as in::

    from paste.deploy.converters import asbool
    setting = asbool(global_conf.get('the_setting'))

"""

from tg.configuration import AppConfig, config

import luci
import sqlalchemy
from luci import model
from luci.lib import app_globals, helpers
from luci.lib.db_helpers import update_db_objects

class LuciAppConfig(AppConfig):
    def __init__(self):
        self.pylons_extra = {}
        super(LuciAppConfig, self).__init__()

    def after_init_config(self):
        from pylons import config as pylons_config
        for key, item in self.pylons_extra.iteritems():
            pylons_config[key] = item
        del self.pylons_extra

    def setup_sqlalchemy(self):
        from pylons import config as pylons_config
        from sqlalchemy import engine_from_config
        engine = engine_from_config(pylons_config, 'sqlalchemy.')
        config['pylons.app_globals'].sa_engine = engine
        self.package.model.init_model(engine)
        try:
            update_db_objects()
        except:
            pass

base_config = LuciAppConfig()
base_config.package = luci
base_config.renderers = []

# Set genshi as the default renderer, forced to generate xhtml output
# (due to problem with TurboGears < 2.1.1 vs. Genshi >= 0.6 generating
# xml by default, see https://bugzilla.redhat.com/show_bug.cgi?id=663103)
base_config.default_renderer = 'genshi'
base_config.renderers.append('genshi')
base_config.pylons_extra['templating.genshi.method'] = 'xhtml'

# Configure the base SQLAlchemy Setup
base_config.use_sqlalchemy = True
base_config.sqlalchemy = {"poolclass": sqlalchemy.pool.NullPool}
base_config.model = luci.model
base_config.DBSession = luci.model.DBSession
