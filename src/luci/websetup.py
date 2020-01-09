# -*- coding: utf-8 -*-
"""Setup the luci application"""

import logging

import transaction
from tg import config

from luci.config.environment import load_environment

__all__ = ['setup_app']

log = logging.getLogger(__name__)

def setup_app(command, conf, vars):
    """Place any commands to setup luci here"""
    load_environment(conf.global_conf, conf.local_conf)
    # Load the models
    from luci import model
    print "Creating tables"
    model.metadata.create_all(bind=config['pylons.app_globals'].sa_engine)

    group = model.Group()
    group.group_name = u'managers'
    group.display_name = u'Administrators'

    model.DBSession.add(group)

    create_group = model.Group()
    create_group.group_name = u'create_cluster'
    create_group.display_name = u'May Create New Clusters'
    model.DBSession.add(create_group)

    import_group = model.Group()
    import_group.group_name = u'import_cluster'
    import_group.display_name = u'May Import Existing Clusters'
    model.DBSession.add(import_group)

    permission = model.Permission()
    permission.permission_name = u'manage'
    permission.description = u'This permission gives an administrative right to the bearer'
    permission.groups.append(group)

    model.DBSession.add(permission)
    model.DBSession.flush()
    transaction.commit()
    print "Successfully setup"
