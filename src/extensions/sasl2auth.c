/*
** Copyright (C) Red Hat, Inc. 2010
**
** This program is free software; you can redistribute it and/or modify it
** under the terms of the GNU General Public License version 2 as
** published by the Free Software Foundation.
**
** This program is distributed in the hope that it will be useful, but
** WITHOUT ANY WARRANTY; without even the implied warranty of
** MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
** General Public License for more details.
**
** You should have received a copy of the GNU General Public License
** along with this program; see the file COPYING. If not, write to the
** Free Software Foundation, Inc., 675 Mass Ave, Cambridge,
** MA 02139, USA.
*/

/*
 * This program is used so we can authenticate via SASL library using
 * saslauthd (presumably against PAM if this authentication mechanism was
 * passed to saslauthd at its start) from a non-root Python application.
 *
 * Author: Chris Feist <cfeist@redhat.com>
 */

#include <Python.h>
#include <sasl/sasl.h>
#include <string.h>

#include "sasl2auth.h"


/* If the use of getopt callback is not explicitly requested
 * by defining following macro, only the configuration file
 * (usually /etc/sasl2/<appname>.conf) is taken as a possible
 * source of options
 */
#ifdef USE_GETOPT_CALLBACK
static int sasl_getopt_callback(void *context,
                                const char *plugin_name,
                                const char *option,
                                const char **result,
                                unsigned *len)
{
    static const char authd_option[] = "pwcheck_method";
    static const char authd_result[] = "saslauthd";
    /* This seems to be obsolete (Cyrus SASL 1 -> 2 transition around 2004)
    static const char authd_version_option[] = "saslauthd_version";
    static const char authd_version_result[] = "2";
    */

    if (result) {
        *result = '\0';
        if (!strcmp(option, authd_option))
            *result = authd_result;
        /*
        else if (!strcmp(option, authd_version_option))
            *result = authd_version_result;
        */
    }

    if (len)
        *len = 0;

    return SASL_OK;
}

static sasl_callback_t callbacks[] = {
    { SASL_CB_GETOPT, (int (*)()) sasl_getopt_callback, NULL }
};
#else
static sasl_callback_t const *callbacks = NULL;
#endif

static int authenticate(const char *username,
                        const char *password,
                        const char *serverFQDN,
                        const char *user_realm,
                        const char *iplocalport,
                        const char *ipremoteport)
{
    int ret;
    sasl_conn_t *conn;

    ret = sasl_server_init(callbacks, LUCI_APPNAME);
    if (ret != SASL_OK)
        return 0;

    ret = sasl_server_new(LUCI_SERVICE,
            serverFQDN, user_realm, iplocalport, ipremoteport,
            NULL, 0, &conn);

    if (ret != SASL_OK)
        return 0;

    ret = sasl_checkpass(conn, username, strlen(username),
                         password, strlen(password));
    if (ret == SASL_OK)
        return 1;

    return 0;
}

static PyObject *sasl2auth_checkauth(PyObject *self, PyObject *args)
{
    const char *username;
    const char *password;
    const char *serverFQDN;
    const char *user_realm;
    const char *iplocalport;
    const char *ipremoteport;

    if (!PyArg_ParseTuple(args, "sszzzz", &username, &password, &serverFQDN, &user_realm, &iplocalport, &ipremoteport))
        return NULL;

    if (authenticate(username, password, serverFQDN, user_realm, iplocalport, ipremoteport))
        return Py_BuildValue("i", 1);

    /* Failure */
    return Py_BuildValue("i", 0);
}

static PyMethodDef Sasl2authMethods[] = {
    {"checkauth", sasl2auth_checkauth, METH_VARARGS, "Authenticate using saslauthd (presumably against PAM)"},
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC initsasl2auth(void)
{
    (void) Py_InitModule("sasl2auth", Sasl2authMethods);
}
