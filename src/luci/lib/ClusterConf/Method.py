# Copyright (C) 2006-2012 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

from TagObject import TagObject
from Device import Device

import logging
log = logging.getLogger(__name__)

TAG_NAME = "method"

class Method(TagObject):
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME

  def getMethodDevices(self):
    ret = list()
    for i in self.getChildren():
      if type(i) is not Device:
        if not i.errors:
          i.errors = True
          log.error('Error parsing cluster XML: expected device element, got %s' % i.getTagName())
      else:
        ret.append(i)
    return ret
