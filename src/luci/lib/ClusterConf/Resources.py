# Copyright (C) 2006-2009 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

from TagObject import TagObject

TAG_NAME = "resources"

class Resources(TagObject):
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME
