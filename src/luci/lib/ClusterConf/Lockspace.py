# Copyright (C) 2010-2011 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

from TagObject import TagObject

TAG_NAME = 'lockspace'

class Lockspace(TagObject):
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME

  def getNodir(self):
    return self.getBinaryAttribute('nodir')

  def setNodir(self, val):
    return self.addBinaryAttribute('nodir', val, ('0', '1'))

  def delNodir(self):
    return self.removeAttribute('nodir')

  def getMaster(self, master_name):
    for i in self.children:
        if i.getName() == master_name:
            return i
    return None

  def delMaster(self, master_name):
    del_node = None
    for i in self.children:
        if i.getName() == master_name:
            del_node = i
            break
    if del_node is not None:
        self.removeChild(del_node)
        return True
    return False
        
  def addMaster(self, master_node):
    self.addChild(master_node)
