# -*- coding: utf-8 -*-

"""Main Controller"""
from tg import expose, flash, require, url, request, redirect, tmpl_context
from repoze.what.predicates import not_anonymous, Any, All, NotAuthorizedError, is_user, in_any_group, in_group

from luci.lib.helpers import ugettext as _
from luci.lib.base import BaseController
from luci.lib.cluster_permissions import permission_remove
from luci.lib.flash2 import Flash2, flash2

from luci.controllers.error import ErrorController
from luci.controllers.cluster import ClusterController
from luci.controllers.async import AsyncController

import luci.validation.validate_cluster_prop as vcp
from luci.lib.db_helpers import db_remove_cluster, grant_all_cluster_roles

__all__ = ['RootController']


# Imports into module's namespace.


class RootController(BaseController):
    """
    The root controller for the luci application.

    All the other controllers and WSGI applications should be mounted on this
    controller. For example::

        panel = ControlPanelController()
        another_app = AnotherWSGIApplication()

    Keep in mind that WSGI applications shouldn't be mounted directly: They
    must be wrapped around with :class:`tg.controllers.WSGIAppController`.

    """

    def __call__(self, environ, start_response):
        """Invoke the Controller"""

        # Register flash2 component for thread/request-local use.
        environ['paste.registry'].register(flash2, Flash2())

        tmpl_context.title_list = []
        tmpl_context.already_used = dict()
        tmpl_context.already_used.setdefault(False)
        return BaseController.__call__(self, environ, start_response)

    # SUBCONTROLLERS

    error = ErrorController()
    cluster = ClusterController()
    async = AsyncController()

    # METHODS OF THE ROOT CONTROLLER

    @expose('luci.templates.index')
    def index(self):
        """Handle the front-page."""
        tmpl_context.show_sidebar = True
        redirect('/homebase/')
        return dict(page='index')

    @expose('luci.templates.about')
    def about(self):
        """Handle the 'about' page."""
        return dict(page='about')

    @expose('luci.templates.prefs')
    def prefs(self):
        """Handle the user preferences page."""
        return dict(page='prefs')

    @expose('luci.templates.admin')
    @require(Any(is_user('root'), in_group('managers'),
            msg=_("User must be an administrator to access this area")))
    def admin(self, name=None):
        """Handle the user permissions page."""
        return dict(page='admin',name=name)

    @expose('luci.templates.admin')
    @require(Any(is_user('root'), in_group('managers'),
            msg=_("User must be an administrator to access this area")))
    def admin_cmd(self, name=None, **args):
        command = args.get('command')
        if not command:
            flash(_("No command was given"), status="error")
            return dict(page='admin')

        if command == 'create':
            ret = vcp.validate_add_user(name, **args)
            if ret[0] is False:
                if ret[1].has_key('errors'):
                    flash(','.join(ret[1]['errors']), status="error")
            else:
                flash(_("User %s created") % name)
                return dict(page='admin',name=name)
        elif command == 'perms':
            """Handle the user permissions form submissions."""
            ret = vcp.validate_user_perms(name, **args)
            if ret[0] is False:
                if ret[1].has_key('errors'):
                    flash(','.join(ret[1]['errors']), status="error")
            else:
                flash(_("Permissions Updated"))
            return dict(page='admin',name=name)
        elif command == 'log':
            ret = vcp.validate_luci_log_levels(**args)
            if ret[0] is False:
                if ret[1].has_key('errors'):
                    flash(','.join(ret[1]['errors']), status="error")
            else:
                flash(_("Settings Applied"))
        return dict(page='admin')

    @expose('luci.templates.homebase')
    @require(not_anonymous())
    def homebase(self, homebasepage='homebasepage', **args):
        tmpl_context.show_sidebar = True
        tmpl_context.homebase = True
        tmpl_context.cluster = []
        return dict(page='homebase', homebasepage=homebasepage, args=args,
                    base_url='/cluster')

    @expose('luci.templates.homebase')
    @require(All(not_anonymous(),
                 Any(is_user('root'),
                     in_any_group('managers', 'import_cluster')),
             msg=_("You must be an administrator or be granted access to import clusters")))
    def add_existing_cmd(self, **args):
        username = None
        try:
            identity = request.environ.get('repoze.who.identity')
            username = identity['repoze.who.userid']
        except:
            username = None

        vret = vcp.validate_add_existing(**args)
        if vret[0] is True:
            if username and username != 'root':
                try:
                    grant_all_cluster_roles(username, args.get('clustername'))
                except:
                    pass
            msgs = vret[1].get('flash')
            if msgs and len(msgs) > 0:
                flash(', '.join(msgs))
        else:
            msgs = vret[1].get('errors')
            if msgs and len(msgs) > 0:
                flash(', '.join(msgs), status="error")
        redirect('/homebase')

    @expose('luci.templates.homebase')
    @require(not_anonymous())
    def manage_remove_cmd(self, **args):
        errors = []
        success = []
        for k, v in args.items():
            try:
                permission_remove(k)
                if db_remove_cluster(k) is not True:
                    errors.append(k)
                else:
                    success.append(k)
            except NotAuthorizedError, e:
                flash(e, status="warning")

        if len(errors) != 0:
            flash(_("Unable to remove cluster %s from the luci interface")
                % (', '.join(errors)), status="error")
        if len(success) != 0:
            flash(_("Removed cluster %s from the luci interface")
                % (', '.join(errors)), status="info")
        redirect('/homebase')

    @expose('luci.templates.cluster')
    def clusters(self, **args):
      redirect('/cluster')

    @expose('luci.templates.login')
    def login(self, came_from=url('/')):
        """Start the user login."""
        login_counter = request.environ['repoze.who.logins']
        if login_counter > 0:
            flash(_('Wrong credentials'), 'warning')
        return dict(page='login', login_counter=str(login_counter),
                    came_from=came_from)

    @expose()
    def post_login(self, came_from=url('/')):
        """
        Redirect the user to the initially requested page on successful
        authentication or redirect her back to the login page if login failed.

        """
        if not request.identity:
            login_counter = request.environ['repoze.who.logins'] + 1
            redirect('/login', came_from=came_from, __logins=login_counter)
        redirect(came_from)

    @expose()
    def post_logout(self, came_from=url('/')):
        """
        Redirect the user to the initially requested page on logout and say
        goodbye as well.

        """
        redirect(came_from)
