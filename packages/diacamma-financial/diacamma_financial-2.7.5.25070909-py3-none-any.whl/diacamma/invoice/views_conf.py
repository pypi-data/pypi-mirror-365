# -*- coding: utf-8 -*-
'''
diacamma.invoice views_conf package

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

from django.utils.translation import gettext_lazy as _

from lucterios.framework.xferadvance import XferListEditor, TITLE_MODIFY, TITLE_DELETE, TITLE_ADD
from lucterios.framework.xferadvance import XferAddEditor
from lucterios.framework.xferadvance import XferDelete
from lucterios.framework.tools import ActionsManage, MenuManage, CLOSE_NO, SELECT_MULTI, SELECT_SINGLE, FORMTYPE_MODAL
from lucterios.framework.xfercomponents import XferCompButton, XferCompLabelForm, XferCompCheckList
from lucterios.framework.xfergraphic import XferContainerAcknowledge
from lucterios.framework import signal_and_lock
from lucterios.CORE.parameters import Params
from lucterios.CORE.views import ParamEdit, ObjectImport
from lucterios.CORE.models import Parameter

from lucterios.contacts.models import CustomField, Individual
from lucterios.contacts.tools import ContactSelection

from diacamma.accounting.tools import correct_accounting_code
from diacamma.invoice.models import Vat, Article, Category, StorageArea, \
    AccountPosting, AutomaticReduce, CategoryBill, MultiPrice
from diacamma.accounting.system import accounting_system_ident


def fill_params(xfer, param_lists=None, is_mini=False):
    if param_lists is None:
        param_lists = ['invoice-vat-mode', 'invoice-default-sell-account', 'invoice-reduce-account',
                       'invoice-account-third', 'invoice-reduce-allow-article-empty']
    Params.fill(xfer, param_lists, 1, xfer.get_max_row() + 1)
    btn = XferCompButton('editparam')
    btn.set_is_mini(is_mini)
    btn.set_location(1, xfer.get_max_row() + 1, 2, 1)
    btn.set_action(xfer.request, ParamEdit.get_action(TITLE_MODIFY, short_icon='mdi:mdi-pencil-outline'), close=CLOSE_NO, params={'params': param_lists})
    xfer.add_component(btn)


MenuManage.add_sub("invoice.conf", "core.extensions", short_icon='mdi:mdi-invoice-outline', caption=_("Invoice"), pos=5)


@MenuManage.describ('invoice.change_vat', FORMTYPE_MODAL, 'invoice.conf', _('Management of parameters and financial configuration of invoice'))
class InvoiceConfFinancial(XferListEditor):
    short_icon = "mdi:mdi-credit-card-settings-outline"
    model = Vat
    field_id = 'vat'
    caption = _("Invoice financial configuration")

    def fillresponse_header(self):
        self.new_tab(_('Parameters'))
        fill_params(self)
        self.new_tab(_('Account posting codes'))
        self.fill_grid(self.get_max_row(), AccountPosting, 'accountposting', AccountPosting.objects.all())
        self.new_tab(_('VAT'))


@MenuManage.describ('CORE.add_parameter')
class InvoiceCommercialParamEdit(ParamEdit):

    def fillresponse(self, params=(), nb_col=1):
        ParamEdit.fillresponse(self, params=params, nb_col=nb_col)
        comp_fields = self.get_components("invoice-custom-field-in-array")
        if comp_fields is not None:
            self.remove_component("invoice-custom-field-in-array")
            new_comp_fields = XferCompCheckList("invoice-custom-field-in-array")
            new_comp_fields.description = comp_fields.description
            new_comp_fields.simple = 2
            new_comp_fields.set_location(comp_fields.col, comp_fields.row, comp_fields.colspan, comp_fields.rowspan)
            new_comp_fields.set_select([(field.get_fieldname(), field.name) for field in CustomField.get_filter(Article)])
            new_comp_fields.set_value(Article.get_custom_fields())
            self.add_component(new_comp_fields)


@MenuManage.describ('invoice.change_vat', FORMTYPE_MODAL, 'invoice.conf', _('Management of commercial configuration of invoice'))
class InvoiceConfCommercial(XferListEditor):
    short_icon = "mdi:mdi-credit-card-settings-outline"
    model = AutomaticReduce
    field_id = 'automaticreduce'
    caption = _("Invoice commercial configuration")

    def add_general_params(self):
        param_lists = ['invoice-article-with-picture', 'invoice-reduce-with-ratio',
                       'invoice-custom-field-in-bill', 'invoice-order-mode', 'invoice-asset-mode',
                       'invoice-default-nbpayoff', 'invoice-default-send-pdf',
                       'invoice-custom-field-in-array']
        row = self.get_max_row() + 1
        Params.fill(self, param_lists, 1, row)
        comp_fields = self.get_components("invoice-custom-field-in-array")
        comp_fields.set_value([field.name for field in CustomField.get_filter(Article) if field.get_fieldname() in Article.get_custom_fields()])
        btn = XferCompButton('editparam')
        btn.set_is_mini(False)
        btn.set_location(3, row, 2, 2)
        btn.set_action(self.request, InvoiceCommercialParamEdit.get_action(TITLE_MODIFY, short_icon='mdi:mdi-pencil-outline'), close=CLOSE_NO, params={'params': param_lists})
        self.add_component(btn)
        self.params['basic_model'] = 'invoice.Article'

    def add_cart_params(self):
        param_lists = ['invoice-cart-active']
        if Params.getvalue('invoice-cart-active'):
            param_lists.extend(['invoice-cart-article-filter', 'invoice-cart-default-category', 'invoice-cart-timeout', 'invoice-cart-email-subject', 'invoice-cart-email-body', 'invoice-cart-default-comment'])
        row = self.get_max_row() + 1
        Params.fill(self, param_lists, 1, row)
        btn = XferCompButton('editcartparam')
        btn.set_is_mini(False)
        btn.set_location(1, row + 10)
        btn.set_action(self.request, ParamEditCart.get_action(TITLE_MODIFY, short_icon='mdi:mdi-pencil-outline'), close=CLOSE_NO, params={'params': param_lists})
        self.add_component(btn)

    def fillresponse_header(self):
        self.new_tab(_('Parameters'))
        self.add_general_params()
        self.new_tab(_('Categories'))
        self.fill_grid(self.get_max_row(), Category, 'category', Category.objects.all())
        self.new_tab(_("Custom field"))
        self.fill_grid(0, CustomField, "custom_field", CustomField.get_filter(Article))
        grid_custom = self.get_components('custom_field')
        grid_custom.delete_header('model_title')
        self.new_tab(_('Storage area'))
        self.fill_grid(self.get_max_row(), StorageArea, 'storagearea', StorageArea.objects.all())
        self.new_tab(_('Category bill'))
        self.fill_grid(self.get_max_row(), CategoryBill, 'categoryBill', CategoryBill.objects.all())
        self.new_tab(_('Cart'))
        self.add_cart_params()
        self.new_tab(_('Multi-price'))
        self.fill_grid(self.get_max_row(), MultiPrice, 'multiprice', MultiPrice.objects.all())
        self.new_tab(_('Automatic reduce'))


@MenuManage.describ('CORE.add_parameter')
class ParamEditCart(ParamEdit):

    def fillresponse(self, params=(), nb_col=1):
        ParamEdit.fillresponse(self, params=params, nb_col=nb_col)
        if Params.getvalue('invoice-cart-active'):
            comment = XferCompLabelForm('comment')
            comment.set_value(_('Use variable in email:{[br/]} - {[b]}#reference:{[/b]}identifier of proof{[br/]} - {[b]}#name:{[/b]}name of recipient{[br/]} - {[b]}#doc:{[/b]}name of documentation sended{[br/]} - {[b]}#nb:{[/b]}number of quotation created{[br/]}'))
            comment.set_color("green")
            comment.set_location(1, self.get_max_row() + 1)
            self.add_component(comment)


@ActionsManage.affect_grid(TITLE_ADD, short_icon='mdi:mdi-pencil-plus-outline')
@ActionsManage.affect_grid(TITLE_MODIFY, short_icon='mdi:mdi-pencil-outline', unique=SELECT_SINGLE)
@MenuManage.describ('invoice.add_vat')
class AccountPostingAddModify(XferAddEditor):
    short_icon = "mdi:mdi-credit-card-settings-outline"
    model = AccountPosting
    field_id = 'accountposting'
    caption_add = _("Add account posting code")
    caption_modify = _("Modify account posting code")


@ActionsManage.affect_grid(TITLE_DELETE, short_icon='mdi:mdi-delete-outline', unique=SELECT_MULTI)
@MenuManage.describ('invoice.delete_vat')
class AccountPostingDel(XferDelete):
    short_icon = "mdi:mdi-credit-card-settings-outline"
    model = AccountPosting
    field_id = 'accountposting'
    caption = _("Delete account posting code")


@ActionsManage.affect_grid(TITLE_ADD, short_icon='mdi:mdi-pencil-plus-outline')
@ActionsManage.affect_grid(TITLE_MODIFY, short_icon='mdi:mdi-pencil-outline', unique=SELECT_SINGLE)
@MenuManage.describ('invoice.add_vat')
class AutomaticReduceAddModify(XferAddEditor):
    short_icon = "mdi:mdi-credit-card-settings-outline"
    model = AutomaticReduce
    field_id = 'automaticreduce'
    caption_add = _("Add automatic reduce")
    caption_modify = _("Modify automatic reduce")


@ActionsManage.affect_grid(TITLE_DELETE, short_icon='mdi:mdi-delete-outline', unique=SELECT_MULTI)
@MenuManage.describ('invoice.delete_vat')
class AutomaticReduceDel(XferDelete):
    short_icon = "mdi:mdi-credit-card-settings-outline"
    model = AutomaticReduce
    field_id = 'automaticreduce'
    caption = _("Delete automatic reduce")


@ActionsManage.affect_grid(TITLE_ADD, short_icon='mdi:mdi-pencil-plus-outline')
@ActionsManage.affect_grid(TITLE_MODIFY, short_icon='mdi:mdi-pencil-outline', unique=SELECT_SINGLE)
@MenuManage.describ('invoice.add_vat')
class MultiPriceAddModify(XferAddEditor):
    short_icon = "mdi:mdi-credit-card-settings-outline"
    model = MultiPrice
    field_id = 'multiprice'
    caption_add = _("Add multi-price")
    caption_modify = _("Modify multi-price")


@ActionsManage.affect_grid(TITLE_DELETE, short_icon='mdi:mdi-delete-outline', unique=SELECT_MULTI)
@MenuManage.describ('invoice.delete_vat')
class MultiPriceDel(XferDelete):
    short_icon = "mdi:mdi-credit-card-settings-outline"
    model = MultiPrice
    field_id = 'multiprice'
    caption = _("Delete multi-price")


@MenuManage.describ('invoice.add_vat')
class StorageAreaSaveContact(XferContainerAcknowledge):
    short_icon = "mdi:mdi-credit-card-settings-outline"
    model = StorageArea
    field_id = 'storagearea'
    methods_allowed = ('PUT',)

    def fillresponse(self, individual=0):
        self.item.contact = Individual.objects.get(id=individual)
        self.item.save()


@MenuManage.describ('invoice.add_vat')
class StorageAreaChangeContact(ContactSelection):
    short_icon = "mdi:mdi-account-cash-outline"
    caption = _("Change manager")
    select_class = StorageAreaSaveContact
    inital_model = Individual
    field_id = 'individual'
    model = Individual
    readonly = False
    methods_allowed = ('POST', 'PUT')


@ActionsManage.affect_grid(TITLE_ADD, short_icon='mdi:mdi-pencil-plus-outline')
@ActionsManage.affect_grid(TITLE_MODIFY, short_icon='mdi:mdi-pencil-outline', unique=SELECT_SINGLE)
@MenuManage.describ('invoice.add_vat')
class StorageAreaAddModify(XferAddEditor):
    short_icon = "mdi:mdi-credit-card-settings-outline"
    model = StorageArea
    field_id = 'storagearea'
    caption_add = _("Add storage area")
    caption_modify = _("Modify storage area")

    def fillresponse(self):
        XferAddEditor.fillresponse(self)
        comp_designation = self.get_components("designation")
        comp_designation.colspan = 2
        self.get_components("name").colspan = 2
        self.filltab_from_model(comp_designation.col, comp_designation.row, True, ['contact'])
        btn = XferCompButton('change_contact')
        btn.set_is_mini(True)
        btn.set_location(comp_designation.col + 1, comp_designation.row)
        btn.set_action(self.request, StorageAreaChangeContact.get_action(_("change"), short_icon='mdi:mdi-pencil-outline'), close=CLOSE_NO)
        self.add_component(btn)
        self.move_components("designation", 0, 1)


@ActionsManage.affect_grid(TITLE_DELETE, short_icon='mdi:mdi-delete-outline', unique=SELECT_MULTI)
@MenuManage.describ('invoice.delete_vat')
class StorageAreaDel(XferDelete):
    short_icon = "mdi:mdi-credit-card-settings-outline"
    model = StorageArea
    field_id = 'storagearea'
    caption = _("Delete storage area")


@ActionsManage.affect_grid(TITLE_ADD, short_icon='mdi:mdi-pencil-plus-outline')
@ActionsManage.affect_grid(TITLE_MODIFY, short_icon='mdi:mdi-pencil-outline', unique=SELECT_SINGLE)
@MenuManage.describ('invoice.add_vat')
class VatAddModify(XferAddEditor):
    short_icon = "mdi:mdi-credit-card-settings-outline"
    model = Vat
    field_id = 'vat'
    caption_add = _("Add VAT")
    caption_modify = _("Modify VAT")


@ActionsManage.affect_grid(TITLE_DELETE, short_icon='mdi:mdi-delete-outline', unique=SELECT_MULTI)
@MenuManage.describ('invoice.delete_vat')
class VatDel(XferDelete):
    short_icon = "mdi:mdi-credit-card-settings-outline"
    model = Vat
    field_id = 'vat'
    caption = _("Delete VAT")


@ActionsManage.affect_grid(TITLE_ADD, short_icon='mdi:mdi-pencil-plus-outline')
@ActionsManage.affect_grid(TITLE_MODIFY, short_icon='mdi:mdi-pencil-outline', unique=SELECT_SINGLE)
@MenuManage.describ('invoice.add_vat')
class CategoryAddModify(XferAddEditor):
    short_icon = "mdi:mdi-credit-card-settings-outline"
    model = Category
    field_id = 'category'
    caption_add = _("Add category")
    caption_modify = _("Modify category")


@ActionsManage.affect_grid(TITLE_DELETE, short_icon='mdi:mdi-delete-outline', unique=SELECT_MULTI)
@MenuManage.describ('invoice.delete_vat')
class CategoryDel(XferDelete):
    short_icon = "mdi:mdi-credit-card-settings-outline"
    model = Category
    field_id = 'category'
    caption = _("Delete Category")


@ActionsManage.affect_grid(TITLE_ADD, short_icon='mdi:mdi-pencil-plus-outline')
@ActionsManage.affect_grid(TITLE_MODIFY, short_icon='mdi:mdi-pencil-outline', unique=SELECT_SINGLE)
@MenuManage.describ('invoice.add_vat')
class CategoryBillAddModify(XferAddEditor):
    short_icon = "mdi:mdi-credit-card-settings-outline"
    model = CategoryBill
    field_id = 'categoryBill'
    caption_add = _("Add category")
    caption_modify = _("Modify category")

    def fillresponse(self):
        if self.item.id is None:
            self.item.fill_default()
            if self.getparam('is_default') is None:
                self.item.is_default = (CategoryBill.objects.filter(is_default=True).count() == 0)
                self.params['is_default'] = 1 if self.item.is_default else 0
        XferAddEditor.fillresponse(self)


@ActionsManage.affect_grid(TITLE_DELETE, short_icon='mdi:mdi-delete-outline', unique=SELECT_MULTI)
@MenuManage.describ('invoice.delete_vat')
class CategoryBillDel(XferDelete):
    short_icon = "mdi:mdi-credit-card-settings-outline"
    model = CategoryBill
    field_id = 'categoryBill'
    caption = _("Delete Category")


@ActionsManage.affect_grid(_("Default"), short_icon='mdi:mdi-star-outline', unique=SELECT_SINGLE)
@MenuManage.describ('invoice.add_vat')
class CategoryBillDefault(XferContainerAcknowledge):
    caption = _("Set default category")
    short_icon = "mdi:mdi-credit-card-settings-outline"
    model = CategoryBill
    field_id = 'categoryBill'

    def fillresponse(self):
        self.item.change_has_default()


@MenuManage.describ('contacts.add_article', FORMTYPE_MODAL, 'invoice.conf', _('Tool to import articles from CSV file.'))
class ArticleImport(ObjectImport):
    caption = _("Article import")
    short_icon = "mdi:mdi-credit-card-settings-outline"

    def get_select_models(self):
        return Article.get_select_contact_type(True)


@signal_and_lock.Signal.decorate('compte_no_found')
def comptenofound_invoice(known_codes, accompt_returned, cost_returned):
    article_unknown = Article.objects.filter(isdisabled=False).exclude(sell_account__in=known_codes).values_list('sell_account', flat=True)
    vat_unknown = Vat.objects.filter(isactif=True).exclude(account__in=known_codes).values_list('account', flat=True)
    param_unknown = Parameter.objects.filter(name__in=('invoice-default-sell-account', 'invoice-reduce-account')).exclude(value__in=known_codes).values_list('value', flat=True)
    comptenofound = ""
    if (len(article_unknown) > 0):
        comptenofound = _("articles") + ":" + ",".join(set(article_unknown)) + " "
    if (len(vat_unknown) > 0):
        comptenofound += _("VAT") + ":" + ",".join(set(vat_unknown))
    if (len(param_unknown) > 0):
        comptenofound += _("parameters") + ":" + ",".join(set(param_unknown))
    if comptenofound != "":
        accompt_returned.append("- {[i]}{[u]}%s{[/u]}: %s{[/i]}" % (_('Invoice'), comptenofound))
    posting_badcost = AccountPosting.objects.filter(cost_accounting__isnull=False, cost_accounting__year__isnull=False, cost_accounting__year__is_actif=False)
    if (len(posting_badcost) > 0):
        cost_returned.append("- {[i]}{[u]}%s{[/u]}: %s{[/i]}" % (_('Account posting code'), ",".join(set([str(posting) for posting in posting_badcost]))))
    return True


@signal_and_lock.Signal.decorate('param_change')
def paramchange_invoice(params):
    invoice_params = ['invoice-default-sell-account', 'invoice-reduce-account', 'invoice-account-third']
    if 'accounting-sizecode' in params:
        for param_item in invoice_params:
            Parameter.change_value(param_item, correct_accounting_code(Params.getvalue(param_item)))
        Params.clear()
        for acc_post in AccountPosting.objects.all():
            if acc_post.sell_account != correct_accounting_code(acc_post.sell_account):
                acc_post.sell_account = correct_accounting_code(acc_post.sell_account)
                acc_post.save()
    for invoice_param in invoice_params:
        if invoice_param in params:
            code_value = Params.getvalue(invoice_param)
            if code_value != "":
                Parameter.change_value(invoice_param, correct_accounting_code(code_value))
    if 'accounting-system' in params:
        system_ident = accounting_system_ident(Params.getvalue("accounting-system"))
        if system_ident == "french":
            Parameter.change_value('invoice-default-sell-account', correct_accounting_code('706'))
            Parameter.change_value('invoice-reduce-account', correct_accounting_code('709'))
            Parameter.change_value("invoice-account-third", correct_accounting_code('411'))
        elif system_ident == "belgium":
            Parameter.change_value('invoice-default-sell-account', correct_accounting_code('700'))
            Parameter.change_value('invoice-reduce-account', correct_accounting_code('708'))
            Parameter.change_value("invoice-account-third", correct_accounting_code('400'))
    Params.clear()


@signal_and_lock.Signal.decorate('conf_wizard')
def conf_wizard_invoice(wizard_ident, xfer):
    if isinstance(wizard_ident, list) and (xfer is None):
        wizard_ident.append(("invoice_params", 25))
        wizard_ident.append(("invoice_vat", 26))
    elif (xfer is not None) and (wizard_ident == "invoice_params"):
        xfer.add_title(_("Diacamma invoice"), _('Parameters'), _('Configuration of parameters'))
        fill_params(xfer, ['invoice-default-sell-account', 'invoice-reduce-account', 'invoice-account-third'], True)
    elif (xfer is not None) and (wizard_ident == "invoice_vat"):
        xfer.add_title(_("Diacamma invoice"), _('VAT'), _('Configuration of vat'))
        fill_params(xfer, ['invoice-vat-mode'], True)
        xfer.fill_grid(10, Vat, 'vat', Vat.objects.all())
        xfer.get_components("vat").colspan = 4
