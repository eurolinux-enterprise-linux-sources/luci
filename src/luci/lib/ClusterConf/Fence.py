# Copyright (C) 2006-2011 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

from TagObject import TagObject

TAG_NAME = "fence"

class Fence(TagObject):
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME

  def findMethod(self, method_name):
    for m in xrange(len(self.children)):
        cur_m = self.children[m]
        if cur_m.getName() == method_name:
            return m
    return None

  def moveMethodUp(self, method_index):
    cur_method = self.children.pop(method_index)
    self.children.insert(method_index - 1, cur_method)

  def moveMethodDown(self, method_index):
    cur_method = self.children.pop(method_index)
    self.children.insert(method_index + 1, cur_method)
