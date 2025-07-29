# -*- coding: utf-8 -*-
'''
Generic generator of Django urls patern for Lucterios

@author: Laurent GAY
@organization: sd-libre.fr
@contact: info@sd-libre.fr
@copyright: 2015 sd-libre.fr
@license: This file is part of Lucterios.

Lucterios is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Lucterios is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Lucterios.  If not, see <http://www.gnu.org/licenses/>.
'''

from __future__ import unicode_literals
from os.path import join, dirname, basename
import logging
import inspect
import pkgutil

from django.conf.urls import include
from django.urls import re_path
from django.conf import settings
from django.utils.module_loading import import_module
from django.views.static import serve
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.http.response import HttpResponse

from lucterios.framework.docs import defaultDocs
from lucterios.framework.signal_and_lock import Signal
from lucterios.framework.auditlog import LucteriosAuditlogModelRegistry
from lucterios.framework.plugins import PluginManager


def defaultblank(request, *args):
    if request.path == '/favicon.ico':
        if hasattr(settings, 'APPLIS_FAVICON'):
            return serve(request, basename(settings.APPLIS_FAVICON), document_root=dirname(settings.APPLIS_FAVICON))
    return HttpResponse('')


def defaultview(*args):
    from django.shortcuts import redirect
    web_page = settings.DEFAULT_PAGE
    if settings.USE_X_FORWARDED_HOST:
        web_page = settings.FORCE_SCRIPT_NAME + web_page
    return redirect(web_page)


class UrlPatterns(list):

    def __init__(self, *args, **kwargs):
        list.__init__(self, *args, **kwargs)
        from django.contrib import admin
        admin.autodiscover()
        old_path = join(dirname(__file__), 'static', 'lucterios.framework', 'old')
        web_path = join(dirname(__file__), 'static', 'lucterios.framework', 'web')
        self.append(re_path(r'^$', defaultview))
        self.append(re_path(r'^favicon.ico$', defaultblank))
        self.append(re_path(r'^web/$', defaultview))
        self.append(re_path(r'^web/STUB/(.*)$', defaultblank))
        self.append(re_path(r'^web/(?P<path>.*)$', serve, {'document_root': web_path}))
        self.append(re_path(r'^Docs$', defaultDocs))
        self.append(re_path(r'^admin/', include(admin.site.get_urls())))

    def add_lct_application(self, appname):
        appmodule = import_module(appname)
        is_lucterios_ext = False
        for _, modname, ispkg in pkgutil.iter_modules(appmodule.__path__):
            if (modname[:5] == 'views') and not ispkg:
                view = import_module(appname + '.' + modname)
                for obj in inspect.getmembers(view):
                    try:
                        if obj[1].url_text != '':
                            if inspect.isclass(obj[1]):
                                is_lucterios_ext = True
                                as_view_meth = getattr(obj[1], "as_view")
                                self.append(re_path(r"^%s$" % obj[1].url_text, as_view_meth()))
                    except AttributeError:
                        pass
            elif settings.APPLIS_MODULE == appmodule:
                is_lucterios_ext = True
        return is_lucterios_ext

    def add_ext_application(self, appname):
        try:
            patterns = getattr(import_module('%s.urls' % appname), 'urlpatterns', None)
            if isinstance(patterns, (list, tuple)):
                for url_pattern in patterns:
                    module_items = appname.split('.')
                    if module_items[0] == 'lucterios':
                        continue
                    if module_items[0] == 'django':
                        self.append(url_pattern)
                    else:
                        try:
                            self.append(re_path(r"^%s/%s" % (module_items[-1], url_pattern.pattern._regex[1:]),
                                                url_pattern.callback, None, url_pattern.pattern.name))
                        except AttributeError:
                            print('-- error', appname, url_pattern.pattern, url_pattern.pattern.name)
        except ImportError:
            pass

    def add_plugins(self):
        for plugin_item in PluginManager.get_instance():
            for view_item in plugin_item.views:
                self.append(re_path(r"^%s$" % view_item.url_text, view_item.as_view()))

    def add_extra_url(self):
        try:
            from django.contrib.admin.sites import site
            self.append(re_path(r'^accounts/login/$', site.login))
        except ImportError:
            pass
        self.extend(staticfiles_urlpatterns())
        self.extend(settings.EXTRA_URL)


def request_config():
    try:
        from django.http import request
        from django.utils.regex_helper import _lazy_re_compile
        if hasattr(request, "host_validation_re"):
            setattr(request, "host_validation_re", _lazy_re_compile(r"^([a-z0-9.-_]+|\[[a-f0-9]*:[a-f0-9\.:]+\])(:\d+)?$"))
    except Exception:
        logging.getLogger('lucterios.core.init').exception("Error to config request")


def get_url_patterns():
    url_patterns = UrlPatterns()
    for appname in settings.INSTALLED_APPS:
        if not url_patterns.add_lct_application(appname):
            url_patterns.add_ext_application(appname)
    url_patterns.add_plugins()
    url_patterns.add_extra_url()
    logging.getLogger('lucterios.core.init').debug("Urls:" + '\n'.join(str(res_item) for res_item in url_patterns))
    Signal.call_signal("get_url_patterns", url_patterns)
    Signal.call_signal("auditlog_register")
    Signal.call_signal("scheduler_refresh")
    LucteriosAuditlogModelRegistry.main_enabled()
    request_config()
    return url_patterns


urlpatterns = get_url_patterns()
