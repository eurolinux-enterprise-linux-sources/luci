# Copyright (C) 2006-2010 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

from BaseResource import BaseResource
from gettext import gettext as _

TAG_NAME = 'clusterfs'
RESOURCE_TYPE = _('GFS')

class Clusterfs(BaseResource):
  def __init__(self):
    BaseResource.__init__(self)
    self.TAG_NAME = TAG_NAME
    self.resource_type = RESOURCE_TYPE

  # If it's a GFS2 filesystem we want to make sure
  # the resource type is GFS2, not GFS
  def addAttribute(self, name, value):
    if name == "fstype" and value == "gfs2":
        self.resource_type = "GFS2"
    BaseResource.addAttribute(self, name, value)
