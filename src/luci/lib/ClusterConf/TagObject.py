# Copyright (C) 2006-2011 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

TAG_NAME = "document"

class TagObject(object):
  def __init__(self, tagname=TAG_NAME):
    self.attr_hash = {}
    self.children = list()
    self.TAG_NAME = tagname
    self.comments = list()
    self.trailing_comments = list()
    self.element_text = None
    self.errors = False

  def addChild(self, child):
    self.children.append(child)

  def removeChild(self, child):
    self.children.remove(child)

  def removeAttribute(self, key):
    try:
        del self.attr_hash[key]
    except:
        return False
    return True

  def addAttribute(self, name, value):
    if value is None:
        return self.removeAttribute(name)
    self.attr_hash[name] = unicode(value)
    return value

  def addIntegerAttribute(self, name, val, bounds=(None, None)):
    if val is None:
        self.removeAttribute(name)
        return None
    int_val = int(val)
    if bounds and type(bounds) is tuple:
        if len(bounds) > 0 and bounds[0] is not None:
            if int_val < bounds[0]:
                raise ValueError, '%d not >= %d' % (int_val, bounds[0])
        if len(bounds) > 1 and bounds[1] is not None:
            if int_val > bounds[1]:
                raise ValueError, '%d not <= %d' % (int_val, bounds[1])
    return self.addAttribute(name, unicode(val))

  def addBinaryAttribute(self, name, value, mapping):
    if value is None:
        self.removeAttribute(name)
        return None
    val_type = type(value)
    if val_type in (str, unicode):
        value = value.lower()
        if value in ('1', 'true', 'on', 'enabled', 'yes'):
            ret = True
        elif value in ('0', 'false', 'off', 'disabled', 'no'):
            ret = False
        else:
            value = int(value)
            if value == 0:
                ret = False
            else:
                ret = True
    elif val_type is bool:
        ret = value
    elif val_type in (int, long, float, complex):
        if value == 0:
            ret = False
        else:
            ret = True
    else:
        raise TypeError, val_type

    new_val = mapping[ret]
    if new_val is None:
        self.removeAttribute(name)
    else:
        self.attr_hash[name] = unicode(new_val)
    return new_val

  def getBinaryAttribute(self, key):
    ret = self.attr_hash.get(key)
    if ret is None:
        return None
    ret = ret.lower()
    if ret in ('1', 'true', 'yes', 'on', 'enable'):
        return True
    if ret in ('0', 'false', 'no', 'off', 'disable'):
        return False
    raise ValueError, ret

  def exportAttributes(self, tag):
    self.removeDefaults()
    for k, v in self.attr_hash.iteritems():
        tag.setAttribute(k, v)

  def emptyTag(self):
    if len(self.comments) == 0 and len(self.trailing_comments) == 0 and len(self.attr_hash) == 0 and not self.element_text:
       return True
    return False

  def generateXML(self, doc, parent=None):
    children_empty = True

    if parent is None:
        parent = doc

    for c in self.comments:
        parent.appendChild(doc.createComment(c))

    tag = doc.createElement(self.TAG_NAME)
    self.exportAttributes(tag)

    for child in self.children:
        if child is not None:
            if child.generateXML(doc, tag) is not False:
                children_empty = False

    for c in self.trailing_comments:
        tag.appendChild(doc.createComment(c))

    if self.element_text:
        tag.appendChild(doc.createTextNode(self.element_text))

    if self.emptyTag() and children_empty is True:
        return False
    
    parent.appendChild(tag)
    return True

  def getAttributes(self):
    return self.attr_hash

  def getAttribute(self, key):
    return self.attr_hash.get(key)

  def getChildren(self):
    """Returns copy of children's list."""
    return self.children[:]

  def getName(self):
    return self.attr_hash.get('name', '')

  def setName(self, val):
    self.attr_hash['name'] = val
    return val

  def getTagName(self):
    return self.TAG_NAME

  def isRefObject(self):
    return False

  def searchTree(self, objlist, tagtype):
    if self.TAG_NAME == tagtype:
      objlist.append(self)
    if len(self.children) > 0:
      for child in self.children:
        if child is None:
          continue
        child.searchTree(objlist, tagtype)

  def replaceChild(self, oldchild, newchild):
    """Looks up oldchild and replace it with newchild."""
    idx = self.children.index(oldchild)
    self.children[idx] = newchild

  def clone(self):
    """Creates a shallow copy of itself."""
    ret = self.__class__ ()
    ret.TAG_NAME = self.TAG_NAME
    ret.attr_hash = self.attr_hash.copy()
    ret.children = self.children
    return ret

  def removeDefaults(self):
    pass
