# Copyright (C) 2008-2009 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

from BaseResource import BaseResource
from gettext import gettext as _

TAG_NAME = 'ASEHAagent'
RESOURCE_TYPE = _('Sybase ASE Failover Instance')

class SybaseASE(BaseResource):
  def __init__(self):
    BaseResource.__init__(self)
    self.TAG_NAME = TAG_NAME
    self.resource_type = RESOURCE_TYPE
