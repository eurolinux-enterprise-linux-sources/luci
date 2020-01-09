# Copyright (C) 2010-2010 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

from BaseResource import BaseResource
from gettext import gettext as _

TAG_NAME = 'orainstance'
RESOURCE_TYPE = _('Oracle 10g Failover Instance')

class OracleInstance(BaseResource):
  def __init__(self):
    BaseResource.__init__(self)
    self.TAG_NAME = TAG_NAME
    self.resource_type = RESOURCE_TYPE
