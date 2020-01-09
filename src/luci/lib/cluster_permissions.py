# Copyright (C) 2011 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

# -*- coding: utf-8 -*-
from tg import request
from repoze.what.predicates import in_any_group, is_user, Any

from luci.lib.helpers import ugettext as _

def permission_view(name):
    Any(is_user('root'), in_any_group('managers', 'view_%s' % name),
        msg=_("You must be an administrator or be granted view access to this cluster")).check_authorization(request.environ)

def permission_node_cmd(name):
    Any(is_user('root'), in_any_group('managers', 'node_cmd_%s' % name),
        msg=_("You must be an administrator or be granted access to modify cluster node state")).check_authorization(request.environ)

def permission_membership(name):
    Any(is_user('root'), in_any_group('managers', 'membership_%s' % name),
        msg=_("You must be an administrator or be granted access to modify cluster membership")).check_authorization(request.environ)

def permission_config(name):
    Any(is_user('root'), in_any_group('managers', 'config_%s' % name),
        msg=_("You must be an administrator or be granted access to modify cluster configuration")).check_authorization(request.environ)

def permission_svc_cmd(name):
    Any(is_user('root'), in_any_group('managers', 'service_cmd_%s' % name),
        msg=_("You must be an administrator or be granted access to modify service group state")).check_authorization(request.environ)

def permission_remove(name):
    Any(is_user('root'), in_any_group('managers', 'remove_%s' % name),
        msg=_("You must be an administrator or be granted access to remove clusters from the management interface")).check_authorization(request.environ)
