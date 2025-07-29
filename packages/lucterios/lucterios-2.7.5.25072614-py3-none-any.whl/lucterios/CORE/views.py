# -*- coding: utf-8 -*-
'''
View for manage user password, print model and label in Lucterios

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
from os.path import isfile, join, dirname, basename
from logging import getLogger
from copy import deepcopy
from base64 import b64decode
import binascii
import mimetypes
import stat
import os

from django.utils.translation import gettext_lazy as _
from django.utils.http import http_date
from django.http.response import StreamingHttpResponse, HttpResponse
from django.apps.registry import apps
from django.conf import settings
from django.db.models import Q

from lucterios.framework.tools import MenuManage, FORMTYPE_NOMODAL, WrapAction, \
    ActionsManage, FORMTYPE_REFRESH, SELECT_SINGLE, CLOSE_NO, FORMTYPE_MODAL, CLOSE_YES, SELECT_MULTI, \
    get_format_from_field, get_icon_path
from lucterios.framework.xferbasic import XferContainerMenu, XferContainerAbstract
from lucterios.framework.xfergraphic import XferContainerAcknowledge, XferContainerCustom, XFER_DBOX_INFORMATION
from lucterios.framework.xfercomponents import XferCompPassword, XferCompImage, XferCompLabelForm, XferCompGrid, XferCompSelect, \
    XferCompMemo, XferCompFloat, XferCompXML, XferCompEdit, XferCompDownLoad, XferCompUpLoad, XferCompButton, XferCompStep
from lucterios.framework.xferadvance import XferListEditor, XferAddEditor, XferDelete, XferSave, TITLE_MODIFY, TITLE_DELETE, \
    TITLE_CLONE, TITLE_OK, TITLE_CANCEL, TITLE_CLOSE, TEXT_TOTAL_NUMBER, action_list_sorted, \
    TITLE_CREATE, TITLE_ADD
from lucterios.framework.error import LucteriosException, IMPORTANT
from lucterios.framework.filetools import get_user_dir, xml_validator, read_file, md5sum
from lucterios.framework import signal_and_lock, tools

from lucterios.CORE.parameters import Params, secure_mode_connect, notfree_mode_connect
from lucterios.CORE.models import Parameter, Label, PrintModel, SavedCriteria, LucteriosUser, LucteriosGroup, ShortCut
from lucterios.CORE.views_usergroup import UsersList, GroupsList
from lucterios.CORE.import_drivers import ImportDriver


MenuManage.add_sub('core.menu', None, short_icon='mdi:mdi-circle-small')
MenuManage.add_sub('core.general', None, short_icon='mdi:mdi-home', caption=_('General'), desc=_('Generality'), pos=1)
MenuManage.add_sub('core.shortcut', 'core.general', short_icon='mdi:mdi-menu-open', caption=_('Short-cut'), desc=_('Short-cut menus customized'), pos=100)
MenuManage.add_sub('core.admin', None, short_icon='mdi:mdi-tune-vertical', caption=_('Management'), desc=_('Manage settings and configurations.'), pos=100)


def right_status(request):
    return signal_and_lock.Signal.call_signal("summary", request) > 0


@MenuManage.describ(right_status, FORMTYPE_MODAL, 'core.menu', _("Summary"))
class StatusMenu(XferContainerCustom):
    caption = _("Summary")
    short_icon = "mdi:mdi-information-slab-box-outline"
    methods_allowed = ('GET', )

    def fillresponse(self):
        signal_and_lock.Signal.call_signal("summary", self)


def right_situation(request):
    return signal_and_lock.Signal.call_signal("situation", request) > 0


@MenuManage.describ(right_situation, FORMTYPE_MODAL, 'core.menu', _("Situation"))
class SituationMenu(XferContainerCustom):
    caption = _("Situation")
    short_icon = "mdi:mdi-information-slab-circle-outline"
    methods_allowed = ('GET', )

    def fillresponse(self):
        signal_and_lock.Signal.call_signal("situation", self)


@MenuManage.describ('')
class Unlock(XferContainerAcknowledge):
    short_icon = 'mdi:mdi-circle-small'
    caption = 'unlock'
    methods_allowed = ('POST', 'PUT', 'GET', 'DELETE')

    def fillresponse(self):
        signal_and_lock.RecordLocker.unlock(self.request, self.params)


signal_and_lock.unlocker_view_class = Unlock


@MenuManage.describ('')
class Download(XferContainerAbstract):
    short_icon = 'mdi:mdi-circle-small'
    methods_allowed = ('GET', 'POST', 'PUT')

    def request_handling(self, request, *args, **kwargs):
        getLogger("lucterios.core.request").debug(">> %s %s [%s]", request.method, request.path, request.user)
        try:
            self._initialize(request, *args, **kwargs)
            try:
                full_path = b64decode(str(self.getparam('filename'))).decode()
            except binascii.Error:
                full_path = join(get_user_dir(), str(self.getparam('filename')))
            sign = self.getparam('sign', '')
            if sign != md5sum(full_path):
                raise LucteriosException(IMPORTANT, _("File invalid!"))
            if not isfile(full_path):
                response = HttpResponse(b'')
                response["Content-Length"] = 0
                return response
            content_type, encoding = mimetypes.guess_type(full_path)
            content_type = content_type or 'application/octet-stream'
            statobj = os.stat(full_path)
            response = StreamingHttpResponse(open(full_path, 'rb'), content_type=content_type)
            response["Last-Modified"] = http_date(statobj.st_mtime)
            response['Content-Disposition'] = 'attachment; filename="' + self.getparam('name', basename(full_path)) + '"'
            if stat.S_ISREG(statobj.st_mode):
                response["Content-Length"] = statobj.st_size
            if encoding:
                response["Content-Encoding"] = encoding
            return response
        finally:
            getLogger("lucterios.core.request").debug("<< %s %s [%s]", request.method, request.path, request.user)


@MenuManage.describ('')
class Menu(XferContainerMenu):
    short_icon = 'mdi:mdi-circle-small'
    caption = 'menu'
    methods_allowed = ('GET', )

    def request_handling(self, request, *args, **kwargs):
        getLogger("lucterios.core.request").debug(">> %s %s [%s]", request.method, request.path, request.user)
        try:
            if request.user.is_authenticated or not secure_mode_connect():
                return XferContainerMenu.request_handling(self, request, *args, **kwargs)
            else:
                from lucterios.CORE.views_auth import Authentification
                auth = Authentification()
                return auth.request_handling(request, *args, **kwargs)
        finally:
            getLogger("lucterios.core.request").debug("<< %s %s [%s]", request.method, request.path, request.user)


def right_changepassword(request):
    if request.user.is_authenticated and not settings.USER_READONLY:
        return True
    return False


@MenuManage.describ(right_changepassword, FORMTYPE_MODAL, 'core.general', _("To Change your password."))
class ChangePassword(XferContainerCustom):
    caption = _("Password")
    short_icon = 'mdi:mdi-lock-plus'
    methods_allowed = ('PUT', )

    def fillresponse(self):
        img = XferCompImage('img')
        img.set_value(self.short_icon, '#')
        img.set_location(0, 0, 1, 3)
        self.add_component(img)

        pwd = XferCompPassword('oldpass')
        pwd.set_location(1, 0, 1, 1)
        pwd.security = 0
        pwd.description = _("old password")
        self.add_component(pwd)

        pwd = XferCompPassword('newpass1')
        pwd.set_location(1, 1, 1, 1)
        pwd.description = _("new password")
        self.add_component(pwd)

        pwd = XferCompPassword('newpass2')
        pwd.set_location(1, 2, 1, 1)
        pwd.description = _("new password (again)")
        self.add_component(pwd)

        self.add_action(ModifyPassword.get_action(_('Ok'), short_icon='mdi:mdi-check'))
        self.add_action(WrapAction(TITLE_CANCEL, short_icon='mdi:mdi-cancel'))


@MenuManage.describ(right_changepassword)
class ModifyPassword(XferContainerAcknowledge):
    caption = _("Password")
    short_icon = 'mdi:mdi-lock-plus'

    def fillresponse(self, oldpass='', newpass1='', newpass2=''):
        if not self.request.user.check_password(oldpass):
            raise LucteriosException(IMPORTANT, _("Bad current password!"))

        if newpass1 != newpass2:
            raise LucteriosException(IMPORTANT, _("The passwords are differents!"))
        self.request.user.set_password(newpass1)
        self.request.user.save()
        self.message(_("Password modify"), XFER_DBOX_INFORMATION)


def right_askpassword(request):
    if not notfree_mode_connect() or settings.USER_READONLY:
        return False
    if (signal_and_lock.Signal.call_signal("send_connection", None, None, None) == 0):
        return False
    return not request.user.is_authenticated


@MenuManage.describ(right_askpassword, FORMTYPE_MODAL, 'core.general', _("Password or login forget?"))
class AskPassword(XferContainerCustom):
    caption = _("Ask password")
    short_icon = 'mdi:mdi-lock-plus'

    def fillresponse(self):
        img = XferCompImage('img')
        img.set_value(self.short_icon, '#')
        img.set_location(0, 0, 1, 3)
        self.add_component(img)
        lbl = XferCompLabelForm('lbl_title')
        lbl.set_location(1, 0, 2)
        lbl.set_value_as_header(_("To receive by email your login and a new password."))
        self.add_component(lbl)

        email = XferCompEdit('email')
        email.set_location(1, 1)
        email.mask = r"[^@]+@[^@]+\.[^@]+"
        email.description = _("email")
        self.add_component(email)

        self.add_action(AskPasswordAct.get_action(_('Ok'), short_icon='mdi:mdi-check'))
        self.add_action(WrapAction(TITLE_CANCEL, short_icon='mdi:mdi-cancel'))


@MenuManage.describ(right_askpassword)
class AskPasswordAct(XferContainerAcknowledge):
    caption = _("Ask password")
    short_icon = 'mdi:mdi-lock-plus'

    def fillresponse(self, email=''):
        import re
        if re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None:
            for user in LucteriosUser.objects.filter(email=email):
                user.generate_password()


@signal_and_lock.Signal.decorate('config')
def config_core(setting_list):
    setting_list['00@%s' % _('General')] = ['CORE-connectmode', 'CORE-Wizard', 'CORE-MessageBefore']
    return True


@signal_and_lock.Signal.decorate('auth_action')
def auth_action_core(actions_basic):
    actions_basic.append(AskPassword.get_action(_("Password or login forget?")))


@MenuManage.describ('CORE.change_parameter', FORMTYPE_MODAL, 'core.admin', _("To view and to modify main parameters."))
class Configuration(XferContainerCustom):
    caption = _("Main configuration")
    short_icon = 'mdi:mdi-tune'
    readonly = True
    methods_allowed = ('GET', )

    def fillresponse(self):
        img_title = XferCompImage('img')
        img_title.set_location(0, 0, 1, 10)
        img_title.set_value(self.short_icon, '#')
        self.add_component(img_title)
        lab = XferCompLabelForm('title')
        lab.set_location(1, 0, 3)
        lab.set_value('{[br/]}{[center]}{[b]}{[u]}%s{[/u]}{[/b]}{[/center]}' % _("Software configuration"))
        self.add_component(lab)
        setting_list = {}
        signal_and_lock.Signal.call_signal("config", setting_list)
        for tab_name in sorted(list(setting_list.keys())):
            self.new_tab(tab_name[tab_name.find('@') + 1:])
            Params.fill(self, setting_list[tab_name], 0, 0)
            btn = XferCompButton(tab_name + "_btn")
            btn.set_action(self.request, ParamEdit.get_action(_('Modify'), short_icon='mdi:mdi-pencil-outline'), close=CLOSE_NO, params={'params': setting_list[tab_name]})
            btn.set_location(0, self.get_max_row() + 1)
            self.add_component(btn)
        steplist = get_wizard_step_list()
        if steplist != '':
            self.add_action(ConfigurationWizard.get_action(_("Wizard"), short_icon="mdi:mdi-star-cog-outline"), close=CLOSE_NO, params={'steplist': steplist})
        self.add_action(WrapAction(TITLE_CLOSE, short_icon='mdi:mdi-close'))


@MenuManage.describ('CORE.add_parameter')
class ParamEdit(XferContainerCustom):
    caption = _("Parameters")
    short_icon = 'mdi:mdi-tune'

    def fillresponse(self, params=(), nb_col=1):
        img_title = XferCompImage('img')
        img_title.set_location(0, 0)
        img_title.set_value(self.short_icon, '#')
        self.add_component(img_title)
        lab = XferCompLabelForm('title')
        lab.set_location(1, 0, 2 * nb_col)
        lab.set_value_as_title(_("Edition of parameters"))
        self.add_component(lab)
        Params.fill(self, params, 1, 1, False, nb_col)
        titles = {}
        signal_and_lock.Signal.call_signal('get_param_titles', params, titles)
        for paramname in titles.keys():
            param_item = self.get_components(paramname)
            if param_item is not None:
                param_item.description = titles[paramname]
        self.add_action(ParamSave.get_action(_('Ok'), short_icon='mdi:mdi-check'))
        self.add_action(WrapAction(TITLE_CANCEL, short_icon='mdi:mdi-cancel'))


@MenuManage.describ('CORE.add_parameter')
class ParamSave(XferContainerAcknowledge):
    caption = _("Parameters")
    short_icon = 'mdi:mdi-tune'

    def fillresponse(self, params=()):
        for pname in params:
            pvalue = self.getparam(pname)
            if pvalue is not None:
                Parameter.change_value(pname, pvalue)
        Params.clear()
        signal_and_lock.Signal.call_signal("param_change", params)


MenuManage.add_sub("core.extensions", 'core.admin', short_icon="mdi:mdi-cog-outline", caption=_("_Extensions (conf.)"), desc=_("To manage of modules configurations."), pos=20)
MenuManage.add_sub("core.plugins", 'core.admin', short_icon="mdi:mdi-power-plug-outline", caption=_("Plugins (conf.)"), desc=_("To manage of external plugins."), pos=30)


@MenuManage.describ('CORE.change_parameter', FORMTYPE_MODAL, 'core.extensions', _('Saved criteria list for searching tools'))
class SavedCriteriaList(XferListEditor):
    short_icon = 'mdi:mdi-table-search'
    model = SavedCriteria
    field_id = 'savedcriteria'
    caption = _("Saved criterias")


@MenuManage.describ('CORE.add_parameter')
class SavedCriteriaAddModify(XferAddEditor):
    short_icon = 'mdi:mdi-table-search'
    model = SavedCriteria
    field_id = 'savedcriteria'
    caption_add = _("Add saved criteria")
    caption_modify = _("Modify saved criteria")


@ActionsManage.affect_grid(TITLE_DELETE, short_icon='mdi:mdi-delete-outline', unique=SELECT_MULTI)
@MenuManage.describ('CORE.add_parameter')
class SavedCriteriaDel(XferDelete):
    short_icon = 'mdi:mdi-table-search'
    model = SavedCriteria
    field_id = 'savedcriteria'
    caption = _("Delete Saved criteria")


@MenuManage.describ('CORE.change_parameter', FORMTYPE_MODAL, 'core.extensions', _('Short-cut list for added menus'))
class ShortCutList(XferListEditor):
    short_icon = 'mdi:mdi-menu-open'
    model = ShortCut
    field_id = 'shortcut'
    caption = _("Short-cut")

    def fillresponse(self):
        XferListEditor.fillresponse(self)
        grid = self.get_components('shortcut')
        grid.change_type_header('icon', 'icon')


@ActionsManage.affect_grid(_('Up'), short_icon="mdi:mdi-arrow-up-bold-outline", unique=SELECT_SINGLE)
@MenuManage.describ('CORE.add_parameter')
class ShortCuttUp(XferContainerAcknowledge):
    short_icon = 'mdi:mdi-menu-open'
    model = ShortCut
    field_id = 'shortcut'
    caption = _("Up short-cut")

    def fillresponse(self):
        self.item.up_order()


@ActionsManage.affect_grid(TITLE_ADD, short_icon='mdi:mdi-pencil-plus-outline')
@ActionsManage.affect_grid(TITLE_MODIFY, short_icon='mdi:mdi-pencil-outline', unique=SELECT_SINGLE)
@MenuManage.describ('CORE.add_parameter')
class ShortCutAddModify(XferAddEditor):
    short_icon = 'mdi:mdi-menu-open'
    model = ShortCut
    field_id = 'shortcut'
    caption_add = _("Add saved short-cut")
    caption_modify = _("Modify short-cut")

    def fillresponse(self):
        if self.item.id is None:
            self.item.icon = self.short_icon
        XferAddEditor.fillresponse(self)


@ActionsManage.affect_grid(TITLE_DELETE, short_icon='mdi:mdi-delete-outline', unique=SELECT_MULTI)
@MenuManage.describ('CORE.add_parameter')
class ShortCutDel(XferDelete):
    short_icon = 'mdi:mdi-menu-open'
    model = ShortCut
    field_id = 'shortcut'
    caption = _("Delete short-cut")


MenuManage.add_sub("core.print", 'core.admin', short_icon='mdi:mdi-printer-pos-cog-outline', caption=_("Report and print"), desc=_("To manage reports and tools of printing."), pos=30)


@MenuManage.describ('CORE.change_printmodel', FORMTYPE_NOMODAL, 'core.print', _("To Manage printing templates."))
class PrintModelList(XferListEditor):
    caption = _("Print templates")
    short_icon = 'mdi:mdi-printer-pos-plus'
    model = PrintModel
    field_id = 'print_model'

    def fillresponse_header(self):
        modelname = self.getparam('modelname', "")
        lab = XferCompLabelForm('lblmodelname')
        lab.set_location(0, 1)
        lab.set_value_as_name(_('model'))
        self.add_component(lab)
        model_list = {}
        for print_model in PrintModel.objects.all():
            if print_model.modelname not in model_list.keys():
                try:
                    model_list[print_model.modelname] = print_model.model_associated_title()
                    if modelname == '':
                        modelname = print_model.modelname
                except LookupError:
                    pass
        model_list = list(model_list.items())
        model_list.sort(key=lambda item: item[1])
        model_sel = XferCompSelect('modelname')
        model_sel.set_location(1, 1)
        model_sel.set_select(model_list)
        model_sel.set_value(modelname)
        model_sel.set_action(self.request, self.return_action("", ""), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        self.add_component(model_sel)
        self.filter = Q(modelname=modelname)
        self.fieldnames = ['name', 'kind', 'is_default']
        return


@ActionsManage.affect_grid(TITLE_MODIFY, short_icon='mdi:mdi-pencil-outline', unique=SELECT_SINGLE)
@MenuManage.describ('CORE.add_printmodel')
class PrintModelEdit(XferContainerCustom):
    caption_add = _("Add a print model")
    caption_modify = _("Modify a print model")
    short_icon = 'mdi:mdi-printer-pos-plus'
    model = PrintModel
    field_id = 'print_model'

    def fill_menu_memo(self, memo_comp):
        for name, value in self.item.model_associated().get_all_print_fields():
            memo_comp.add_sub_menu(name, value)

    def _fill_from_kind(self):
        self.item.mode = int(self.item.mode)
        if self.item.kind == 1:
            self.fill_from_model(2, 3, False, ['mode'])
            self.get_components('mode').set_action(self.request, self.return_action('', ''), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
            if (self.item.mode == 1) and (self.item.value[:6] != '<model'):
                self.item.value = "<model>\n<body>\n<text>%s</text></body>\n</model>" % self.item.value
        if self.item.kind == 0:
            self._fill_listing_editor()
        elif (self.item.kind == 1) and (self.item.mode == 0):
            self._fill_label_editor()
        elif (self.item.kind == 2) or ((self.item.kind == 1) and (self.item.mode == 1)):
            self._fill_report_editor()

    def fillresponse(self):
        img_title = XferCompImage('img')
        img_title.set_location(0, 0, 1, 6)
        img_title.set_value(self.short_icon, '#')
        self.add_component(img_title)
        lab = XferCompLabelForm('title')
        lab.set_location(1, 0, 2)
        lab.set_value_as_title(_("Print models"))
        self.add_component(lab)
        self.fill_from_model(2, 1, False, ['name'])
        self.fill_from_model(2, 2, True, ['kind'])
        self._fill_from_kind()
        for act, opt in ActionsManage.get_actions(ActionsManage.ACTION_IDENT_EDIT, self, key=action_list_sorted):
            self.add_action(act, **opt)
        self.add_action(WrapAction(TITLE_CLOSE, short_icon='mdi:mdi-close'))

    def _fill_listing_editor(self):
        edt = XferCompFloat('page_width', 0, 9999, 0)
        edt.set_location(2, 3)
        edt.set_value(self.item.page_width)
        edt.description = _("list page width")
        self.add_component(edt)
        edt = XferCompFloat('page_heigth', 0, 9999, 0)
        edt.set_location(2, 4)
        edt.set_value(self.item.page_height)
        edt.description = _("list page height")
        self.add_component(edt)

        lab = XferCompLabelForm('lbl_col_size')
        lab.set_location(1, 5)
        lab.set_value_as_infocenter(_("size"))
        self.add_component(lab)
        lab = XferCompLabelForm('lbl_col_title')
        lab.set_location(2, 5)
        lab.set_value_as_infocenter(_("title"))
        self.add_component(lab)
        lab = XferCompLabelForm('lbl_col_text')
        lab.set_location(3, 5)
        lab.set_value_as_infocenter(_("text"))
        self.add_component(lab)

        col_index = 0
        for col_size, col_title, col_text in (self.item.columns + [[0, '', ''], [0, '', ''], [0, '', '']]):
            edt = XferCompFloat('col_size_%d' % col_index, 0, 999, 0)
            edt.set_location(1, 6 + col_index)
            edt.set_value(col_size)
            self.add_component(edt)
            edt = XferCompMemo('col_title_%d' % col_index)
            edt.set_location(2, 6 + col_index)
            edt.set_value(col_title)
            edt.set_height(75)
            self.add_component(edt)
            edt = XferCompMemo('col_text_%d' % col_index)
            edt.set_location(3, 6 + col_index)
            edt.set_height(50)
            edt.with_hypertext = True
            edt.set_value(col_text)
            self.fill_menu_memo(edt)
            self.add_component(edt)
            col_index += 1

    def _fill_label_editor(self):
        edit = XferCompMemo('value')
        edit.set_value(self.item.value)
        edit.set_location(2, 4)
        edit.set_height(100)
        edit.with_hypertext = True
        self.fill_menu_memo(edit)
        self.add_component(edit)

    def _fill_report_editor(self):
        edit = XferCompXML('value')
        edit.set_value(self.item.value)
        edit.schema = read_file(join(dirname(dirname(__file__)), 'framework', 'template.xsd'))
        edit.set_location(2, 4)
        edit.set_height(400)
        edit.with_hypertext = True
        self.fill_menu_memo(edit)
        self.add_component(edit)


@ActionsManage.affect_grid(_('Reload'), short_icon='mdi:mdi-reload', close=CLOSE_NO, unique=SELECT_SINGLE)
@ActionsManage.affect_edit(_('Reload'), short_icon='mdi:mdi-reload', close=CLOSE_NO)
@MenuManage.describ('CORE.add_printmodel')
class PrintModelReload(XferContainerAcknowledge):
    caption = _("reload model")
    short_icon = 'mdi:mdi-printer-pos-plus'
    model = PrintModel
    field_id = 'print_model'

    def fillresponse(self):
        model_module = ".".join(self.item.model_associated().__module__.split('.')[:-1])
        if self.getparam('SAVE') is None:
            dlg = self.create_custom(self.model)
            dlg.item = self.item
            img = XferCompImage('img')
            img.set_value(self.short_icon, '#')
            img.set_location(0, 0, 1, 3)
            dlg.add_component(img)
            lbl = XferCompLabelForm('title')
            lbl.set_value_as_title(self.caption)
            lbl.set_location(1, 0, 6)
            dlg.add_component(lbl)

            lbl = XferCompLabelForm('lbl_default_model')
            lbl.set_value_as_name(_("Model to reload"))
            lbl.set_location(1, 1)
            dlg.add_component(lbl)
            sel = XferCompSelect('default_model')
            sel.set_select(PrintModel.get_default_model(model_module, self.item.modelname, self.item.kind))
            sel.set_location(2, 1)
            dlg.add_component(sel)

            dlg.add_action(self.return_action(TITLE_OK, short_icon='mdi:mdi-check'), close=CLOSE_YES, params={'SAVE': 'YES'})
            dlg.add_action(WrapAction(TITLE_CANCEL, short_icon='mdi:mdi-cancel'))
        else:
            if self.item.load_model(model_module, self.getparam("default_model", ""), is_default=None):
                self.message(_('Model reloaded'))


@ActionsManage.affect_edit(_("Import"), short_icon="mdi:mdi-upload-box-outline", close=CLOSE_NO)
@MenuManage.describ('documents.add_folder')
class PrintModelImport(XferContainerAcknowledge):
    caption = _("reload model")
    short_icon = 'mdi:mdi-printer-pos-plus'
    model = PrintModel
    field_id = 'print_model'

    def fillresponse(self):
        if self.getparam('SAVE') is None:
            dlg = self.create_custom(self.model)
            dlg.item = self.item
            img = XferCompImage('img')
            img.set_value(self.short_icon, '#')
            img.set_location(0, 0, 1, 3)
            dlg.add_component(img)
            lbl = XferCompLabelForm('title')
            lbl.set_value_as_title(self.caption)
            lbl.set_location(1, 0, 6)
            dlg.add_component(lbl)

            lbl = XferCompLabelForm('lbl_import_model')
            lbl.set_value_as_name(_("file to load"))
            lbl.set_location(1, 1)
            dlg.add_component(lbl)
            upload = XferCompUpLoad('import_model')
            upload.compress = False
            upload.http_file = True
            upload.maxsize = 128 * 1024 * 1024  # 128Mo
            upload.add_filter('.mdl')
            upload.set_location(2, 1)
            dlg.add_component(upload)

            dlg.add_action(self.return_action(TITLE_OK, short_icon='mdi:mdi-check'), close=CLOSE_YES, params={'SAVE': 'YES'})
            dlg.add_action(WrapAction(TITLE_CANCEL, short_icon='mdi:mdi-cancel'))
        else:
            if 'import_model' in self.request.FILES.keys():
                upload_file = self.request.FILES['import_model']
                if self.item.import_file(upload_file):
                    self.message(_('Model loaded'))


@ActionsManage.affect_edit(_("Extract"), short_icon="mdi:mdi-download-box-outline", close=CLOSE_NO)
@MenuManage.describ('documents.add_folder')
class PrintModelExtract(XferContainerCustom):
    caption = _("Extract")
    short_icon = 'mdi:mdi-printer-pos-plus'
    model = PrintModel
    field_id = 'print_model'

    def fillresponse(self):
        img = XferCompImage('img')
        img.set_value(self.short_icon, '#')
        img.set_location(0, 0, 1, 3)
        self.add_component(img)
        lbl = XferCompLabelForm('title')
        lbl.set_value_as_title(self.caption)
        lbl.set_location(1, 0, 6)
        self.add_component(lbl)
        zipdown = XferCompDownLoad('filename')
        zipdown.compress = False
        zipdown.http_file = True
        zipdown.maxsize = 0
        zipdown.set_value("%s.mdl" % self.item.name)
        zipdown.set_download(self.item.extract_file())
        zipdown.set_location(1, 15, 2)
        self.add_component(zipdown)


@ActionsManage.affect_edit(TITLE_OK, short_icon='mdi:mdi-check', close=CLOSE_YES)
@MenuManage.describ('CORE.add_printmodel')
class PrintModelSave(XferSave):
    caption = _("print model")
    short_icon = 'mdi:mdi-printer-pos-plus'
    model = PrintModel
    field_id = 'print_model'

    def fillresponse(self):
        self.item.mode = int(self.item.mode)
        if self.item.kind == 0:
            page_width = int(self.getparam('page_width'))
            page_heigth = int(self.getparam('page_heigth'))
            columns = []
            col_index = 0
            while self.getparam('col_size_%d' % col_index) is not None:
                col_size = int(self.getparam('col_size_%d' % col_index))
                col_title = self.getparam('col_title_%d' % col_index)
                col_text = self.getparam('col_text_%d' % col_index)
                if col_size > 0:
                    columns.append((col_size, col_title, col_text))
                col_index += 1
            self.item.change_listing(page_width, page_heigth, columns)
            self.item.save()
        elif self.item.kind == 2 or (self.item.kind == 1 and self.item.mode == 1):
            error = xml_validator(self.item.value, join(dirname(dirname(__file__)), 'framework', 'template.xsd'))
            if error is not None:
                raise LucteriosException(IMPORTANT, error)
            self.item.save()
        else:
            XferSave.fillresponse(self)


@ActionsManage.affect_grid(TITLE_CLONE, short_icon='mdi:mdi-content-copy', unique=SELECT_SINGLE)
@MenuManage.describ('CORE.add_printmodel')
class PrintModelClone(XferContainerAcknowledge):
    caption = _("Add a print model")
    short_icon = 'mdi:mdi-printer-pos-plus'
    model = PrintModel
    field_id = 'print_model'

    def fillresponse(self):
        self.item.clone()


@ActionsManage.affect_grid(TITLE_DELETE, short_icon='mdi:mdi-delete-outline', unique=SELECT_SINGLE)
@MenuManage.describ('CORE.delete_printmodel')
class PrintModelDelete(XferDelete):
    caption = _("Delete print model")
    short_icon = 'mdi:mdi-printer-pos-plus'
    model = PrintModel
    field_id = 'print_model'


@ActionsManage.affect_grid(_("Default"), short_icon='mdi:mdi-star-outline', unique=SELECT_SINGLE)
@MenuManage.describ('CORE.add_printmodel')
class PrintModelSetDefault(XferContainerAcknowledge):
    caption = _("Set default print model")
    short_icon = 'mdi:mdi-printer-pos-plus'
    model = PrintModel
    field_id = 'print_model'

    def fillresponse(self):
        self.item.change_has_default()


@MenuManage.describ('CORE.change_label', FORMTYPE_NOMODAL, 'core.print', _("To manage boards of labels"))
class LabelList(XferListEditor):
    caption = _("Labels")
    short_icon = 'mdi:mdi-printer-pos-star'
    model = Label
    field_id = 'label'


@ActionsManage.affect_grid(TITLE_CREATE, short_icon='mdi:mdi-pencil-plus')
@ActionsManage.affect_grid(TITLE_MODIFY, short_icon='mdi:mdi-pencil-outline', unique=SELECT_SINGLE)
@MenuManage.describ('CORE.add_label')
class LabelEdit(XferAddEditor):
    caption_add = _("Add a label")
    caption_modify = _("Modify a label")
    short_icon = 'mdi:mdi-printer-pos-star'
    model = Label
    field_id = 'label'

    def fillresponse(self):
        XferAddEditor.fillresponse(self)
        img = self.get_components('img')
        img.set_value(get_icon_path('images/label_help.png'), '')


@ActionsManage.affect_grid(TITLE_DELETE, short_icon='mdi:mdi-delete-outline', unique=SELECT_MULTI)
@MenuManage.describ('CORE.delete_label')
class LabelDelete(XferDelete):
    caption = _("Delete label")
    short_icon = 'mdi:mdi-printer-pos-star'
    model = Label
    field_id = 'label'


@MenuManage.describ('')
class ObjectMerge(XferContainerAcknowledge):
    caption = _("Merge")
    short_icon = "mdi:mdi-merge"
    model = None
    field_id = 'object'

    def _search_model(self):
        modelname = self.getparam('modelname')
        self.model = apps.get_model(modelname)
        XferContainerAcknowledge._search_model(self)

    def fillresponse(self, field_id):
        self.items = self.model.objects.filter(id__in=self.getparam(field_id, ())).distinct()
        if len(self.items) < 2:
            raise LucteriosException(IMPORTANT, _("Impossible: you must to select many records!"))
        item_id = self.getparam('mrg_' + self.field_id, 0)
        if item_id != 0:
            self.item = self.model.objects.get(id=item_id)
        if (self.item is None) or (self.item.id is None):
            self.item = self.items[0]
        if self.getparam("CONFIRME") is None:
            dlg = self.create_custom()
            lbl = XferCompLabelForm('title')
            lbl.set_value_as_title(self.caption)
            lbl.set_location(1, 0)
            dlg.add_component(lbl)
            grid = XferCompGrid('mrg_' + self.field_id)
            grid.add_header('value', _('designation'))
            grid.add_header('select', _('is main?'), 'B')
            for item in self.items:
                grid.set_value(item.id, 'value', str(item))
                grid.set_value(item.id, 'select', item.id == self.item.id)
            grid.set_location(1, 1)
            grid.add_action(self.request, self.return_action(_("Edit"), short_icon='mdi:mdi-text-box-outline'),
                            modal=FORMTYPE_MODAL, close=CLOSE_NO, unique=SELECT_SINGLE, params={"CONFIRME": 'OPEN'})
            grid.add_action(self.request, self.return_action(_("Select"), short_icon='mdi:mdi-check-bold'),
                            modal=FORMTYPE_REFRESH, close=CLOSE_NO, unique=SELECT_SINGLE)
            dlg.add_component(grid)
            dlg.add_action(self.return_action(_('Ok'), short_icon='mdi:mdi-check'), close=CLOSE_YES, modal=FORMTYPE_MODAL,
                           params={'CONFIRME': 'YES', 'mrg_' + self.field_id: self.item.id})
            dlg.add_action(WrapAction(TITLE_CANCEL, short_icon='mdi:mdi-cancel'))
        elif self.getparam("CONFIRME") == 'YES':
            alias_objects = []
            for item in self.items:
                if item.id != self.item.id:
                    alias_objects.append(item.get_final_child())
            self.item.get_final_child().merge_objects(alias_objects)
            self.redirect_action(ActionsManage.get_action_url(self.model.get_long_name(), 'Show', self), params={field_id: self.item.id})
        else:
            self.redirect_action(ActionsManage.get_action_url(self.model.get_long_name(), 'Show', self), params={field_id: self.item.id})


@MenuManage.describ('')
class ObjectPromote(XferContainerAcknowledge):
    caption = _("Promote")
    short_icon = 'mdi:mdi-tune'
    model = None
    field_id = ''

    def _search_model(self):
        modelname = self.getparam('modelname')
        self.model = apps.get_model(modelname)
        self.field_id = self.getparam('field_id', modelname.lower())
        XferContainerAcknowledge._search_model(self)

    def fillresponse(self):
        if self.getparam("CONFIRME") is None:
            dlg = self.create_custom()
            img = XferCompImage('img')
            img.set_value(self.short_icon, '#')
            img.set_location(0, 0)
            dlg.add_component(img)
            lbl = XferCompLabelForm('title')
            lbl.set_value_as_title(self.caption)
            lbl.set_location(1, 0, 2)
            dlg.add_component(lbl)
            lbl = XferCompLabelForm('lbl_record')
            lbl.set_value_as_name(_('record'))
            lbl.set_location(1, 1)
            dlg.add_component(lbl)
            lbl = XferCompLabelForm('record')
            lbl.set_value(str(self.item))
            lbl.set_location(2, 1)
            dlg.add_component(lbl)
            lbl = XferCompLabelForm('lbl_current')
            lbl.set_value_as_name(_('current model'))
            lbl.set_location(1, 2)
            dlg.add_component(lbl)
            lbl = XferCompLabelForm('current')
            lbl.set_value(self.item.__class__._meta.verbose_name)
            lbl.set_location(2, 2)
            dlg.add_component(lbl)
            lbl = XferCompLabelForm('lbl_newmodel')
            lbl.set_value_as_name(_('new model'))
            lbl.set_location(1, 3)
            dlg.add_component(lbl)
            lbl = XferCompSelect('newmodel')
            lbl.set_select(self.item.__class__.get_select_contact_type(False))
            lbl.set_location(2, 3)
            dlg.add_component(lbl)
            dlg.add_action(self.return_action(_('Ok'), short_icon='mdi:mdi-check'), close=CLOSE_YES, modal=FORMTYPE_MODAL, params={'CONFIRME': 'YES'})
            dlg.add_action(WrapAction(TITLE_CANCEL, short_icon='mdi:mdi-cancel'))
        else:
            new_model = apps.get_model(self.getparam('newmodel'))
            field_id_name = "%s_ptr_id" % self.model.__name__.lower()
            new_object = new_model(**{field_id_name: self.item.pk})
            new_object.save()
            new_object.__dict__.update(self.item.__dict__)
            new_object.save()
            self.redirect_action(ActionsManage.get_action_url(self.model.get_long_name(), 'Show', self))


class ObjectImport(XferContainerCustom):

    def __init__(self, **kwargs):
        XferContainerCustom.__init__(self, **kwargs)
        self.model = None
        self.import_driver = None
        self.items_imported = {}

    def get_select_models(self):
        return []

    def _select_csv_parameters(self):
        driver_select = XferCompSelect('drivername')
        driver_select.set_value(self.import_driver.NAME)
        driver_select.set_select([(drivername, drivername) for drivername in ImportDriver.factory_list()])
        driver_select.set_location(1, 1, 3)
        driver_select.description = _('import driver')
        driver_select.set_action(self.request, self.return_action(), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        self.add_component(driver_select)

        model_select = XferCompSelect('modelname')
        if self.model is not None:
            model_select.set_value(self.model.get_long_name())
        model_select.set_select(self.get_select_models())
        model_select.set_location(1, 2, 3)
        model_select.description = _('model')
        self.add_component(model_select)
        upld = XferCompUpLoad('importcontent')
        upld.http_file = True
        upld.multi_files = True
        upld.set_needed(True)
        upld.add_filter(self.import_driver.EXTENSION)
        upld.set_location(1, 3, 2)
        upld.description = self.import_driver.EXTENSION_TITLE
        self.add_component(upld)
        row = 4
        col = 1
        for fieldname, title in self.import_driver.FIELD_LIST:
            lbl = XferCompEdit(fieldname)
            lbl.set_value(getattr(self.import_driver, fieldname, ''))
            lbl.set_location(col, row)
            lbl.description = title
            self.add_component(lbl)
            col += 1
            if col == 3:
                col = 1
                row += 1

    def _select_fields(self):
        column_names = list(self.import_driver.get_column_names())
        select_list = [('', None)]
        for fieldname in column_names:
            select_list.append((fieldname, fieldname))
        row = 0
        for fieldname in self.model.get_import_fields():
            if isinstance(fieldname, tuple):
                fieldname, title = fieldname
                is_need = False
            else:
                dep_field = self.model.get_field_by_name(fieldname)
                title = dep_field.verbose_name
                is_need = not dep_field.blank and not dep_field.null
                fieldnames = fieldname.split('.')
                if is_need and (len(fieldnames) > 1):
                    init_field = self.model.get_field_by_name(fieldnames[0])
                    if not (init_field.is_relation and init_field.many_to_many):
                        is_need = not init_field.null
            lbl = XferCompSelect('fld_' + fieldname)
            lbl.set_select(deepcopy(select_list))
            lbl.set_value(title if title in column_names else "")
            lbl.set_needed(is_need)
            lbl.set_location(1, row)
            lbl.description = title
            self.add_component(lbl)
            row += 1

    def _show_initial_csv(self):
        tbl = XferCompGrid('Array')
        for fieldname in self.import_driver.get_column_names():
            tbl.add_header(fieldname, fieldname)
        row_idx = 1
        for row in self.import_driver.get_rows():
            for colname, value in row.items():
                tbl.set_value(row_idx, colname, value)
            row_idx += 1
        tbl.set_location(1, 1, 2)
        self.add_component(tbl)
        lbl = XferCompLabelForm('nb_line')
        lbl.set_value(_("Total number of items: %d") % (row_idx - 1))
        lbl.set_location(1, 2, 2)
        self.add_component(lbl)

    def _get_field_info(self, fieldname):
        dep_field = self.model.get_field_by_name(fieldname)
        title = dep_field.verbose_name
        hfield = get_format_from_field(dep_field)
        format_str = "%s"
        if isinstance(hfield, str) and (';' in hfield):
            hfield = hfield.split(';')
            format_str = ";".join(hfield[1:])
            hfield = hfield[0]
        return title, hfield, format_str

    def _read_csv_and_convert(self):
        fields_association = {}
        for param_key in self.params.keys():
            if (param_key[:4] == 'fld_') and (self.params[param_key] != ""):
                fields_association[param_key[4:]] = self.params[param_key]
        fields_description = []
        for fieldname in self.model.get_import_fields():
            format_str = "%s"
            if isinstance(fieldname, tuple):
                fieldname, title = fieldname
                hfield = None
            else:
                title, hfield, format_str = self._get_field_info(fieldname)
            if fieldname in fields_association.keys():
                fields_description.append((fieldname, title, hfield, format_str, fields_association[fieldname]))
        return fields_description

    def _fillcontent_select_fields(self):
        lbl = XferCompLabelForm('modelname')
        lbl.set_value(self.model._meta.verbose_name.title())
        lbl.set_location(1, 1)
        lbl.description = _('model')
        self.add_component(lbl)
        self.import_driver.read(self)
        self.new_tab(_("Fields"))
        self._select_fields()
        self.new_tab(_("Current content"))
        self._show_initial_csv()

    def _fillcontent_preview_import(self):
        lbl = XferCompLabelForm('modelname')
        lbl.set_value(self.model._meta.verbose_name.title())
        lbl.set_location(1, 1)
        lbl.description = _('model')
        self.add_component(lbl)
        fields_description = self._read_csv_and_convert()
        self.import_driver.read(self)
        tbl = XferCompGrid('Array')
        for field_description in fields_description:
            tbl.add_header(field_description[0], field_description[1], field_description[2], formatstr=field_description[3])
        row_idx = 1
        for row in self.import_driver.get_readed_content(fields_description):
            for fieldname, value in row.items():
                tbl.set_value(row_idx, fieldname, value)
            row_idx += 1
        tbl.set_location(1, 2, 2)
        self.add_component(tbl)
        lbl = XferCompLabelForm('nb_line')
        lbl.set_value(_("Total number of items: %d") % (row_idx - 1))
        lbl.set_location(1, 3, 2)
        self.add_component(lbl)

    def _fillcontent_import_result(self):
        def add_item_if_not_null(new_item):
            if new_item is not None:
                self.items_imported[new_item.id] = new_item
        fields_description = self._read_csv_and_convert()
        self.import_driver.read(self)
        self.model.initialize_import()
        self.items_imported = {}
        dateformat = getattr(self.import_driver, "dateformat", "%Y-%m-%d")
        for rowdata in self.import_driver.get_readed_content(fields_description):
            add_item_if_not_null(self.model.import_data(rowdata, dateformat))
        add_item_if_not_null(self.model.finalize_import())
        lbl = XferCompLabelForm('result')
        if len(self.items_imported) == 0:
            lbl.set_value_as_header(_("no item are been imported"))
        elif len(self.items_imported) == 1:
            lbl.set_value_as_header(_("1 item are been imported"))
        else:
            lbl.set_value_as_header(_("%d items are been imported") % len(self.items_imported))
        lbl.set_location(1, 2, 2)
        self.add_component(lbl)
        lbl = XferCompLabelForm('import_error')
        lbl.set_color('red')
        lbl.set_value(self.model.get_import_logs())
        lbl.set_location(1, 3, 2)
        self.add_component(lbl)

    def fillresponse(self, modelname, drivername="CSV", step=1):
        if modelname is not None:
            self.model = apps.get_model(modelname)
        self.import_driver = ImportDriver.factory(drivername)
        for fieldname, _title in self.import_driver.FIELD_LIST:
            if fieldname in self.params:
                setattr(self.import_driver, fieldname, self.params[fieldname])
        img = XferCompImage('img')
        img.set_value(self.short_icon, '#')
        img.set_location(0, 0, 1, 6)
        self.add_component(img)
        stepcomp = XferCompStep('step', 4)
        stepcomp.set_value(step)
        stepcomp.set_action(self.request, self.return_action(), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        stepcomp.set_location(1, 0, 2)
        stepcomp.description = _('import progression')
        self.add_component(stepcomp)
        if step == 1:
            self._select_csv_parameters()
        elif step == 2:
            self._fillcontent_select_fields()
        elif step == 3:
            self._fillcontent_preview_import()
        elif step == 4:
            self._fillcontent_import_result()
        if step < 4:
            self.add_action(WrapAction(TITLE_CANCEL, short_icon='mdi:mdi-cancel'))
        else:
            self.remove_component('step')
            self.add_action(WrapAction(TITLE_CLOSE, short_icon='mdi:mdi-close'))


tools.bad_permission_redirect_classaction = Menu


def right_show_wizard(request):
    return Params.getvalue("CORE-Wizard") and (request.user.is_superuser or not secure_mode_connect())


@MenuManage.describ("CORE.add_parameter")
class ConfigurationWizard(XferListEditor):
    caption = _("Configuration wizard")
    short_icon = "mdi:mdi-star-cog-outline"
    model = None
    field_id = ''
    readonly = True
    methods_allowed = ('POST', )

    def add_name(self, pos, name):
        lbl = XferCompLabelForm('name_%d' % pos)
        lbl.set_centered()
        lbl.set_value_as_name(name)
        lbl.set_location(0, pos)
        self.add_component(lbl)

    def add_title(self, title, subtitle, helptext=''):
        lbl = XferCompLabelForm('title')
        lbl.set_centered()
        lbl.set_value_as_info(title)
        lbl.set_location(0, 3, 6)
        self.add_component(lbl)
        lbl = XferCompLabelForm('subtitle')
        lbl.set_centered()
        lbl.set_value_as_name(subtitle)
        lbl.set_location(0, 4, 6)
        self.add_component(lbl)
        lbl = XferCompLabelForm('help')
        lbl.set_italic()
        lbl.set_value(helptext + "{[br/]}")
        lbl.set_location(0, 5, 6)
        self.add_component(lbl)

    def header_title(self, step, steplist):
        progress = XferCompStep("step", len(steplist))
        progress.set_value(step)
        progress.set_location(0, 0, 6)
        progress.description = _("progress steps")
        progress.set_action(self.request, self.return_action(), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        self.add_component(progress)
        lbl = XferCompLabelForm('sep1')
        lbl.set_value("{[hr/]}")
        lbl.set_location(0, 1, 6)
        self.add_component(lbl)

    def fillresponse(self, step=1, steplist=[]):
        self.header_title(step, steplist)
        signal_and_lock.Signal.call_signal("conf_wizard", steplist[step - 1], self)
        self.add_action(WrapAction(TITLE_CLOSE, short_icon='mdi:mdi-close'))


def get_wizard_step_list():
    wizard_list = []
    signal_and_lock.Signal.call_signal("conf_wizard", wizard_list, None)
    wizard_list.sort(key=lambda item: item[1])
    return ";".join([item[0] for item in wizard_list])


@signal_and_lock.Signal.decorate('summary')
def summary_core(xfer):
    if not hasattr(xfer, 'add_component'):
        return right_show_wizard(xfer) and (get_wizard_step_list() != '') and ConfigurationWizard.get_action().check_permission(xfer)
    elif right_show_wizard(xfer.request):
        steplist = get_wizard_step_list()
        if steplist != '':
            btn = XferCompButton("conf_wizard")
            btn.set_location(0, xfer.get_max_row() + 1, 4)
            btn.set_action(xfer.request, ConfigurationWizard.get_action(
                _("Wizard"), short_icon="mdi:mdi-star-cog-outline"), close=CLOSE_NO, params={'steplist': steplist})
            btn.java_script = """if (typeof Singleton().hide_wizard === 'undefined') {
    current.actionPerformed();
    Singleton().hide_wizard = 1;
}
"""
            xfer.add_component(btn)


@signal_and_lock.Signal.decorate('addon_menu')
def addon_menu_core(request, parentref, resjson):
    if parentref == 'core.shortcut':
        for short_cut in ShortCut.objects.all():
            if short_cut.check_permission(request):
                resjson.append(short_cut.get_action_json())
        return ShortCut.objects.count()
    else:
        return 0


@signal_and_lock.Signal.decorate('conf_wizard')
def conf_wizard_core(wizard_ident, xfer):
    if isinstance(wizard_ident, list) and (xfer is None):
        wizard_ident.append(("core_home", 0))
        wizard_ident.append(("core_users", 100))
    elif (xfer is not None) and (wizard_ident == "core_home"):
        initial_wizard = Params.getvalue("CORE-Wizard")
        param_wizard = xfer.getparam("CORE-Wizard", initial_wizard)
        if initial_wizard != param_wizard:
            Parameter.change_value("CORE-Wizard", param_wizard)
            Params.clear()
        lbl = XferCompLabelForm('title')
        lbl.set_centered()
        lbl.set_value_as_info(str(settings.APPLIS_NAME))
        lbl.set_location(0, 3, 6)
        xfer.add_component(lbl)
        lbl = XferCompImage('img')
        lbl.type = 'jpg'
        lbl.set_value(settings.APPLIS_LOGO)
        lbl.set_location(2, 4, 2)
        xfer.add_component(lbl)
        lbl = XferCompLabelForm('home')
        lbl.set_value(_('This wizard will help you to configure this software.'))
        lbl.set_location(0, 5, 6)
        xfer.add_component(lbl)
        Params.fill(xfer, ['CORE-Wizard'], 1, 6, False)
        check = xfer.get_components("CORE-Wizard")
        check.set_action(xfer.request, xfer.return_action(), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        lbl = XferCompLabelForm('lbl_wizard')
        lbl.set_value_as_name(check.description)
        lbl.set_location(2, 6)
        xfer.add_component(lbl)
        check.description = ""
    elif (xfer is not None) and (wizard_ident == "core_users"):
        xfer.add_title(str(settings.APPLIS_NAME), _("Groups and users"))
        param_lists = ['CORE-connectmode', 'CORE-Wizard']
        Params.fill(xfer, param_lists, 1, xfer.get_max_row() + 1)
        btn = XferCompButton('editparam')
        btn.set_location(4, xfer.get_max_row())
        btn.set_is_mini(True)
        btn.set_action(xfer.request, ParamEdit.get_action(TITLE_MODIFY, short_icon='mdi:mdi-pencil-outline'), close=CLOSE_NO,
                       params={'params': param_lists})
        xfer.add_component(btn)
        lbl = XferCompLabelForm("nb_user")
        lbl.set_location(1, xfer.get_max_row() + 1)
        lbl.set_value(TEXT_TOTAL_NUMBER % {'name': LucteriosUser._meta.verbose_name_plural, 'count': len(LucteriosUser.objects.all())})
        xfer.add_component(lbl)
        btn = XferCompButton("btnusers")
        btn.set_location(4, xfer.get_max_row())
        btn.set_action(xfer.request, UsersList.get_action(TITLE_MODIFY, short_icon='mdi:mdi-pencil-outline'), close=CLOSE_NO)
        xfer.add_component(btn)
        lbl = XferCompLabelForm("nb_group")
        lbl.set_location(1, xfer.get_max_row() + 1)
        lbl.set_value(TEXT_TOTAL_NUMBER % {'name': LucteriosGroup._meta.verbose_name_plural, 'count': len(LucteriosGroup.objects.all())})
        xfer.add_component(lbl)
        btn = XferCompButton("btngroups")
        btn.set_location(4, xfer.get_max_row())
        btn.set_action(xfer.request, GroupsList.get_action(TITLE_MODIFY, short_icon='mdi:mdi-pencil-outline'), close=CLOSE_NO)
        xfer.add_component(btn)
