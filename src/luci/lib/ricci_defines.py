# Copyright (C) 2006-2011 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

LUCI_LOG_DEBUG_NETWORK		= False
LUCI_LOG_DEBUG				= False

RICCI_BATCH_FAILURES_MAX	= 5
RICCI_CONNECT_FAILURES_MAX  = 5

CERTS_DIR_PATH				= '/var/lib/luci/certs/'

DEFAULT_RICCI_PORT			= 11111

REQUEST_TAG					= 'request'
RESPONSE_TAG				= 'response'

FUNC_CALL_TAG				= 'function_call'
FUNC_RESP_TAG				= 'function_response'
SEQUENCE_TAG				= 'sequence'

VARIABLE_TAG				= 'var'

VARIABLE_TYPE_INT			= 'int'
VARIABLE_TYPE_INT_SEL		= 'int_select'
VARIABLE_TYPE_BOOL			= 'boolean'
VARIABLE_TYPE_STRING		= 'string'
VARIABLE_TYPE_STRING_SEL	= 'string_select'
VARIABLE_TYPE_XML			= 'xml'

VARIABLE_TYPE_LIST_INT		= 'list_int'
VARIABLE_TYPE_LIST_STR		= 'list_str'
VARIABLE_TYPE_LIST_XML		= 'list_xml'

VARIABLE_TYPE_LISTENTRY		= 'listentry'
VARIABLE_TYPE_FLOAT			= 'float'
