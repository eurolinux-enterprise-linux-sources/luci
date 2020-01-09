# Copyright (C) 2006-2011 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

from Service import Service
from BaseResource import BaseResource

TAG_NAME = "vm"

vm_attributes = ('migration_mapping', 'xmlfile', 'migrate',
                 'path', 'snapshot', 'hypervisor_uri',
                 'migration_uri', 'status_program')

class Vm(Service, BaseResource):
  def __init__(self):
    Service.__init__(self)
    self.TAG_NAME = TAG_NAME

  def getResourceAttributes(self):
    attrs = self.getAttributes()
    for k in attrs.keys():
        # include subtree attributes, too
        if k[:2] != '__' and not k in vm_attributes:
            del attrs[k]
    return attrs

  def delResourceAttributes(self):
    for i in vm_attributes:
        self.removeAttribute(i)
    self.delSubtreeProperties()
