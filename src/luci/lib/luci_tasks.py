# Copyright (C) 2009-2011 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

TASK_CLUSTER_CREATE            = 1
TASK_CLUSTER_UPDATE_CONF       = 2
TASK_CLUSTER_ADD_NODE          = 3
TASK_CLUSTER_DEL_NODE          = 4
TASK_CLUSTER_START             = 5
TASK_CLUSTER_STOP              = 6
TASK_CLUSTER_RESTART           = 7
TASK_CLUSTER_DELETE            = 8
TASK_CLUSTER_ACTIVATE_CONF     = 9

TASK_CLUSTER_NODE_START        = 100
TASK_CLUSTER_NODE_STOP         = 101
TASK_CLUSTER_NODE_REBOOT       = 102
TASK_CLUSTER_NODE_FENCE        = 103
TASK_CLUSTER_NODE_DELETE       = 104

TASK_CLUSTER_SVC_START         = 1000
TASK_CLUSTER_SVC_RESTART       = 1001
TASK_CLUSTER_SVC_DISABLE       = 1002
TASK_CLUSTER_SVC_RELOCATE      = 1003
TASK_CLUSTER_SVC_MIGRATE       = 1004

# Creating a cluster and adding a node are multi-step luci tasks.
# Below is the order of the ricci commands that are issued. The value defined
# is the index of the action into the ricci batch.
SUBTASK_CREATE_INSTALL        = 1
SUBTASK_CREATE_DISABLE_SVC    = 2
# Reboot is optional
SUBTASK_CREATE_REBOOT         = 3
SUBTASK_CREATE_CONF           = 4
SUBTASK_CREATE_ENABLE_SVC     = 5
SUBTASK_CREATE_START          = 6

def luci_task_blocks_cluster(task_type):
    if task_type < 100:
        return True
    return False
