# Copyright (C) 2009-2011 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

from zope.interface import implements

from repoze.who.interfaces import IAuthenticator, IMetadataProvider

from luci.model import DBSession
from luci.model.auth import User, Group
import transaction

from luci import sasl2auth

import logging
log = logging.getLogger(__name__)

class Sasl2AuthPlugin(object):
    implements(IAuthenticator, IMetadataProvider)

    def __init__(self,
                 server_fqdn=None,
                 user_realm=None,
                 iplocalport=None,
                 ipremoteport=None):
        self.server_fqdn = server_fqdn
        self.user_realm = user_realm
        self.iplocalport = iplocalport
        self.ipremoteport = ipremoteport

    # IAuthenticatorPlugin
    def authenticate(self, environ, identity):
        if not ('login' in identity and 'password' in identity):
            return None

        if sasl2auth.checkauth(
            identity['login'], identity['password'], self.server_fqdn,
            self.user_realm, self.iplocalport, self.ipremoteport
        ):
            username = identity['login']
            try:
                db_user = User.by_user_name(username)
                if not db_user:
                    db_user = User(
                        user_name=username,
                        display_name=username,
                        email_address=username,
                    )
                    try:
                        DBSession.add(db_user)
                        transaction.commit()
                    except:
                        transaction.abort()
                        try:
                            DBSession.rollback()
                        except:
                            log.exception("rollback")
                        log.exception("Creating DB object for user %s" % username)
            except:
                log.exception("Looking up username %s" % username)


            return identity['login']

        return None

    def add_metadata(self, environ, identity):
        permissions = []
        groups = []

        username = identity.get('repoze.who.userid')
        try:
            db_user = User.by_user_name(username)
            if db_user:
                groups = [g.group_name for g in db_user.groups]
        except:
            log.exception("Assembling group list for %s" % username)

        if username == 'root':
            groups.append('managers')
        identity['user'] = username
        identity['groups'] = groups
        identity['permissions'] = permissions
        if 'repoze.what.credentials' not in environ:
            environ['repoze.what.credentials'] = {}
        environ['repoze.what.credentials']['groups'] = groups
        environ['repoze.what.credentials']['permissions'] = permissions
        # Adding the userid:
        userid = identity['repoze.who.userid']
        environ['repoze.what.credentials']['repoze.what.userid'] = userid

from repoze.what.plugins.pylonshq import booleanize_predicates
booleanize_predicates()
