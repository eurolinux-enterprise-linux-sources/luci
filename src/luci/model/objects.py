# Copyright (C) 2009-2011 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

from datetime import datetime

from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Unicode, Integer, DateTime, String
from sqlalchemy.orm import relation

from luci.model import DeclarativeBase, metadata
from luci.model.auth import User

cluster_nodes_table = Table('cluster_nodes', metadata,
    Column('cluster_id', Integer, ForeignKey('clusters.cluster_id'), primary_key=True),
    Column('node_id', Integer, ForeignKey('nodes.node_id'), primary_key=True))

cluster_tasks_table = Table('cluster_tasks', metadata,
    Column('cluster_id', Integer, ForeignKey('clusters.cluster_id'), primary_key=True),
    Column('task_id', Integer, ForeignKey('tasks.task_id'), primary_key=True))

node_tasks_table = Table('node_tasks', metadata,
    Column('node_id', Integer, ForeignKey('nodes.node_id'), primary_key=True),
    Column('task_id', Integer, ForeignKey('tasks.task_id'), primary_key=True))

user_tasks_table = Table('user_tasks', metadata,
    Column('user_id', Integer, ForeignKey('tg_user.user_id'), primary_key=True),
    Column('task_id', Integer, ForeignKey('tasks.task_id'), primary_key=True))

class Task(DeclarativeBase):
    __tablename__ = 'tasks'

    task_id = Column(Integer, autoincrement=True, primary_key=True)
    task_type = Column(Integer)
    batch_id = Column(Integer)
    batch_status = Column(Integer)
    batch_failures = Column(Integer, default=0)
    started = Column(DateTime, default=datetime.now)
    last_status = Column(DateTime, default=datetime.now)
    finished = Column(DateTime)
    description = Column(Unicode(255))
    status_msg = Column(Unicode(255))
    redirect_url = Column(Unicode(512))

    owner = relation(User, secondary=user_tasks_table, backref="user")
    def __repr__(self):
        return '<Task: id=%d batch_id=%d task_type=%d>' \
                % (self.task_id, self.batch_id, self.task_type)
    
    def __unicode__(self):
        return self.task_id


class Node(DeclarativeBase):
    __tablename__ = 'nodes'
    
    #{ Columns
    
    node_id = Column(Integer, autoincrement=True, primary_key=True)
    node_name = Column(Unicode(255), unique=False, nullable=False)
    display_name = Column(Unicode(255))
    hostname = Column(Unicode(255))
    ipaddr = Column(String(39))
    port = Column(Integer)
    
    #{ Relations
    tasks = relation(Task, secondary=node_tasks_table, backref="node",
                single_parent=True, cascade="all, delete-orphan",
                passive_deletes=True)
    
    #{ Special methods
    
    def __repr__(self):
        return '<Node: name=%s, hostname=%s, port=%d>' \
                % (self.node_name, self.hostname, self.port)
    
    def __unicode__(self):
        return self.node_name
    
    #}

class Cluster(DeclarativeBase):
    __tablename__ = 'clusters'
    
    #{ Columns

    cluster_id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(16), unique=True, nullable=False)
    display_name = Column(Unicode(255))
    created = Column(DateTime, default=datetime.now)

    #{ Relations

    nodes = relation(Node, secondary=cluster_nodes_table, backref="cluster",
                single_parent=True, cascade="all, delete-orphan",
                passive_deletes=True)
    tasks = relation(Task, secondary=cluster_tasks_table, backref="cluster",
                single_parent=True, cascade="all, delete-orphan",
                passive_deletes=True)
    
    #{ Special methods

    def __repr__(self):
        return '<Cluster: id="%d" name="%s" display_name="%s">' \
                 % (self.cluster_id, self.name, self.display_name)

    def __unicode__(self):
        return self.display_name or self.name
