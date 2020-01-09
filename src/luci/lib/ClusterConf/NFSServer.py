# Copyright (C) 2010 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

from BaseResource import BaseResource
from gettext import gettext as _

TAG_NAME = 'nfsserver'
RESOURCE_TYPE = _('NFS Server')

DENY_ALL_CHILDREN = True

class NFSServer(BaseResource):
  def __init__(self):
    BaseResource.__init__(self)
    self.TAG_NAME = TAG_NAME
    self.resource_type = RESOURCE_TYPE
    self.deny_all_children = DENY_ALL_CHILDREN
