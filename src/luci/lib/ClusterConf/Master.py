# Copyright (C) 2010 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

from TagObject import TagObject

TAG_NAME = 'master'

class Master(TagObject):
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME

  def getWeight(self):
    return self.getAttribute('weight')

  def setWeight(self, val):
    return self.addIntegerAttribute('weight', val, (0, None))

  def delWeight(self):
    return self.removeAttribute('weight')

