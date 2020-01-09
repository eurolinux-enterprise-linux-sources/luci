# Copyright (C) 2006-2011 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

from BaseResource import BaseResource
from TagObject import TagObject

TAG_NAME = "ref"

class RefObject(BaseResource):
  def __init__(self, obj):
    TagObject.__init__(self)
    self.obj_ptr = obj
    self.TAG_NAME = self.obj_ptr.getTagName()
    self.addAttribute('ref', self.obj_ptr.getName())

    try:
        obj.ref()
        obj.reflist.append(self)
    except:
        pass

  def __del__(self):
    try:
        self.obj_ptr.unref()
        self.obj_ptr.reflist.remove(self)
    except:
        pass

  def ref(self):
    pass

  def unref(self):
    pass

  def getObj(self):
    return self.obj_ptr

  def setRef(self, attr):
    self.addAttribute('ref', attr)

  def isRefObject(self):
    return True

  def getName(self):
    return self.attr_hash.get('ref', '')

  def isDenyAll(self):
    return self.obj_ptr.isDenyAll()
