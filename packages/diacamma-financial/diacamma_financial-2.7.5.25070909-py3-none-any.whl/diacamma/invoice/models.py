# -*- coding: utf-8 -*-
'''
diacamma.invoice models package

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
from re import match
from os.path import exists, join, dirname
from datetime import timedelta
from logging import getLogger
from json import dumps, loads
from json.decoder import JSONDecodeError

from django.db import models
from django.db.models.query import QuerySet
from django.db.models.aggregates import Max, Sum, Count
from django.db.models.functions import Concat
from django.db.models.expressions import Case, When
from django.db.models.fields import FloatField, IntegerField
from django.db.models import Q, Value, F
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils.dateformat import DateFormat
from django.utils import timezone
from django_fsm import FSMIntegerField, transition

from lucterios.framework.models import LucteriosModel, correct_db_field, LucteriosLogEntry
from lucterios.framework.model_fields import get_value_if_choices, LucteriosVirtualField, LucteriosDecimalField, get_obj_contains
from lucterios.framework.error import LucteriosException, IMPORTANT, GRAVE
from lucterios.framework.signal_and_lock import Signal
from lucterios.framework.filetools import get_user_path, readimage_to_base64, remove_accent
from lucterios.framework.tools import same_day_months_after, get_date_formating, format_to_string, convert_date, format_value
from lucterios.framework.auditlog import auditlog
from lucterios.CORE.models import Parameter, SavedCriteria, LucteriosGroup, Preference, LucteriosUser, PrintModel
from lucterios.CORE.parameters import Params
from lucterios.contacts.models import CustomField, CustomizeObject, AbstractContact, Individual

from diacamma.accounting.models import FiscalYear, Third, EntryAccount, CostAccounting, Journal, EntryLineAccount, ChartsAccount, AccountThird, \
    AccountLink
from diacamma.accounting.tools import current_system_account, currency_round, correct_accounting_code, format_with_devise, get_amount_from_format_devise
from diacamma.payoff.models import Supporting, Payoff, BankAccount, BankTransaction, DepositSlip, PaymentMethod


class Vat(LucteriosModel):
    MODE_NOVAT = 0
    MODE_PRICENOVAT = 1
    MODE_PRICEWITHVAT = 2

    name = models.CharField(_('name'), max_length=20)
    rate = models.DecimalField(_('rate'), max_digits=6, decimal_places=2,
                               default=10.0, validators=[MinValueValidator(0.0), MaxValueValidator(99.9)])
    isactif = models.BooleanField(verbose_name=_('is actif'), default=True)
    account = models.CharField(_('vat account'), max_length=50, default='4455')

    def __str__(self):
        return str(self.name)

    @classmethod
    def get_default_fields(cls):
        return ["name", "rate", "account", "isactif"]

    class Meta(object):
        verbose_name = _('VAT')
        verbose_name_plural = _('VATs')


class Category(LucteriosModel):
    name = models.CharField(_('name'), max_length=50)
    designation = models.TextField(_('designation'))

    def __str__(self):
        return str(self.name)

    @classmethod
    def get_default_fields(cls):
        return ["name", "designation"]

    @classmethod
    def get_edit_fields(cls):
        return ["name", "designation"]

    @classmethod
    def get_show_fields(cls):
        return ["name", "designation"]

    class Meta(object):
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        default_permissions = []


class StorageArea(LucteriosModel):
    NO_AREA = 0

    name = models.CharField(_('name'), max_length=50)
    designation = models.TextField(_('designation'))
    contact = models.ForeignKey(Individual, verbose_name=_('manager'), null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return str(self.name)

    @classmethod
    def get_default_fields(cls):
        return ["name", "contact", "designation"]

    @classmethod
    def get_edit_fields(cls):
        return ["name", "designation"]

    @classmethod
    def get_show_fields(cls):
        return ["name", "contact", "designation"]

    class Meta(object):
        verbose_name = _('Storage area')
        verbose_name_plural = _('Storage areas')
        default_permissions = []


class ArticleCustomField(LucteriosModel):
    article = models.ForeignKey('Article', verbose_name=_('article'), null=False, on_delete=models.CASCADE)
    field = models.ForeignKey(CustomField, verbose_name=_('field'), null=False, on_delete=models.CASCADE)
    value = models.TextField(_('value'), default="")

    data = LucteriosVirtualField(verbose_name=_('value'), compute_from=lambda item: item.field.convert_data(item.value))

    def get_auditlog_object(self):
        return self.article.get_final_child()

    class Meta(object):
        verbose_name = _('custom field value')
        verbose_name_plural = _('custom field values')
        default_permissions = []


class AccountPosting(LucteriosModel):
    name = models.CharField(_('name'), max_length=100, blank=False)
    sell_account = models.CharField(_('sell account'), max_length=50, blank=True)
    cost_accounting = models.ForeignKey(CostAccounting, verbose_name=_('cost accounting'), null=True, default=None, on_delete=models.PROTECT)
    provision_third_account = models.CharField(_('provision third account'), max_length=50, blank=True)

    def __str__(self):
        return self.name

    @classmethod
    def get_default_fields(cls):
        return ["name", "sell_account", "cost_accounting"]

    @classmethod
    def get_edit_fields(cls):
        fields = ["name", "sell_account", ("cost_accounting", None)]
        if Params.getvalue('invoice-order-mode') != Bill.INVOICE_ORDER_NONE:
            fields.append("provision_third_account")
        return fields

    @classmethod
    def get_show_fields(cls):
        return ["name", "sell_account", "cost_accounting", "provision_third_account"]

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.sell_account = correct_accounting_code(self.sell_account)
        self.provision_third_account = correct_accounting_code(self.provision_third_account) if self.provision_third_account != '' else ''
        return LucteriosModel.save(self, force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    class Meta(object):
        verbose_name = _('Account posting code')
        verbose_name_plural = _('Account posting codes')
        default_permissions = []


class MultiPrice(LucteriosModel):
    name = models.CharField(_('name'), max_length=250, blank=False)
    filtercriteria = models.ForeignKey(SavedCriteria, verbose_name=_('filter criteria'), null=True, on_delete=models.PROTECT)

    PREFIX_PRICE = "price_"

    def __str__(self):
        return self.name

    @classmethod
    def get_default_fields(cls):
        return ["name", "filtercriteria"]

    @classmethod
    def get_edit_fields(cls):
        return ["name", "filtercriteria"]

    @classmethod
    def get_show_fields(cls):
        return ["name", "filtercriteria"]

    def get_fieldname(self):
        return self.PREFIX_PRICE + "%d" % self.id

    @property
    def filtercriteria_query(self):
        return SavedCriteria.objects.filter(modelname=Third.get_long_name())

    def check_filtercriteria(self, third_id):
        if self.filtercriteria_id is not None:
            if (third_id == 0) or (third_id is None):
                return False
            from lucterios.framework.xfersearch import get_search_query_from_criteria
            filter_result, _desc = get_search_query_from_criteria(self.filtercriteria.criteria, Third)
            third_list = Third.objects.filter(filter_result).distinct()
            return third_list.filter(id=third_id).exists()
        return True

    class Meta(object):
        verbose_name = _('multi-price')
        verbose_name_plural = _('multi-prices')
        default_permissions = []


class MultiPriceValue(LucteriosModel):
    article = models.ForeignKey('Article', verbose_name=_('article'), null=False, on_delete=models.CASCADE)
    multiprice = models.ForeignKey(MultiPrice, verbose_name=_('multi-price'), null=False, on_delete=models.CASCADE)
    price = LucteriosDecimalField(_('price'), max_digits=10, decimal_places=3,
                                  default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(9999999.999)], format_string=lambda: format_with_devise(5))

    price_txt = LucteriosVirtualField(verbose_name=_('price'), compute_from='price', format_string=lambda: format_with_devise(5))

    def get_auditlog_object(self):
        return self.article.get_final_child()

    class Meta(object):
        verbose_name = _('multi-price value')
        verbose_name_plural = _('multi-price values')
        default_permissions = []


class Article(LucteriosModel, CustomizeObject):
    STOCKABLE_NO = 0
    STOCKABLE_YES = 1
    STOCKABLE_YES_WITHOUTSELL = 2
    STOCKABLE_KIT = 4
    LIST_STOCKABLES = ((STOCKABLE_NO, _('no stockable')), (STOCKABLE_YES, _('stockable')), (STOCKABLE_YES_WITHOUTSELL, _('stockable & no marketable')), (STOCKABLE_KIT, _('kit of articles')))

    CustomFieldClass = ArticleCustomField
    FieldName = 'article'

    reference = models.CharField(_('reference'), max_length=30, db_index=True)
    designation = models.TextField(_('designation'))
    price = LucteriosDecimalField(_('price'), max_digits=10, decimal_places=3,
                                  default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(9999999.999)], format_string=lambda: format_with_devise(5))
    unit = models.CharField(_('unit'), null=True, default='', max_length=10)
    isdisabled = models.BooleanField(verbose_name=_('is disabled'), default=False, db_index=True)
    sell_account = models.CharField(_('sell account'), max_length=50)
    vat = models.ForeignKey(Vat, verbose_name=_('vat'), null=True, default=None, on_delete=models.PROTECT)
    stockable = models.IntegerField(verbose_name=_('stockable'), choices=LIST_STOCKABLES, null=False, default=STOCKABLE_NO, db_index=True)
    categories = models.ManyToManyField(Category, verbose_name=_('categories'), blank=True)
    qtyDecimal = models.IntegerField(verbose_name=_('quantity decimal'), default=0, validators=[MinValueValidator(0), MaxValueValidator(3)])
    accountposting = models.ForeignKey(AccountPosting, verbose_name=_('account posting code'), null=True, default=None, on_delete=models.PROTECT)

    stockage_total = LucteriosVirtualField(verbose_name=_('quantities'), compute_from='get_stockage_total')
    booking_total = LucteriosVirtualField(verbose_name=_('booking'), compute_from='get_booking_total')
    available_total = LucteriosVirtualField(verbose_name=_('available'), compute_from='get_available_total')
    price_txt = LucteriosVirtualField(verbose_name=_('price'), compute_from='price', format_string=lambda: format_with_devise(5))
    current_price_txt = LucteriosVirtualField(verbose_name=_('current price'), compute_from='get_current_price', format_string=lambda: format_with_devise(5))

    last_buy_price = LucteriosVirtualField(verbose_name=_('last buy price'), compute_from='get_last_buy_price', format_string=lambda: format_with_devise(5))
    mean_buy_price = LucteriosVirtualField(verbose_name=_('mean buy price'), compute_from='get_mean_buy_price', format_string=lambda: format_with_devise(5))

    def __init__(self, *args, **kwargs):
        LucteriosModel.__init__(self, *args, **kwargs)
        self.show_storagearea = 0
        self.current_third = None

    def set_context(self, xfer):
        self.show_storagearea = xfer.getparam('storagearea', 0)
        if not xfer.request.user.is_anonymous:
            contact = Individual.objects.filter(user=xfer.request.user).first()
            if contact is not None:
                self.current_third = Third.objects.filter(contact=contact).first()

    @staticmethod
    def have_category():
        return LucteriosModel.have_class_item(Category)

    @staticmethod
    def have_vat():
        return (Params.getvalue("invoice-vat-mode") != Vat.MODE_NOVAT) and LucteriosModel.have_class_item(Vat)

    @staticmethod
    def have_storage():
        return LucteriosModel.have_class_item(StorageArea)

    @staticmethod
    def have_provider():
        return Provider().third_query.count() > 0

    def __str__(self):
        return str(self.reference)

    @property
    def kit_article_set(self):
        return RecipeKitArticle.objects.filter(article=self)

    @classmethod
    def get_custom_fields(cls):
        fields = Params.getvalue("invoice-custom-field-in-array").split(";")
        return fields

    def get_text_value(self):
        text_value = self.designation.split('{[br/]}')[0]
        if len(text_value) > 50:
            text_value = text_value[:47] + '...'
        stock_txt = ''
        stockage_values = self.get_stockage_values()
        if len(stockage_values) > 0:
            stock_txt = '(%s%s)' % (stockage_values[-1][2], self.unit)
        return "%s | %s %s" % (self.reference, text_value, stock_txt)

    @classmethod
    def get_field_by_name(cls, fieldname):
        dep_field = CustomizeObject.get_virtualfield(fieldname)
        if dep_field is None:
            dep_field = super(Article, cls).get_field_by_name(fieldname)
        return dep_field

    @classmethod
    def get_default_fields(cls):
        fields = []
        if Params.getvalue("invoice-article-with-picture"):
            fields.append((_('image'), 'image'))
        fields.extend(["reference", "designation", "price", 'unit', "stockable"])
        fields.extend([(field.name, field.get_fieldname()) for field in CustomField.get_filter(Article) if field.get_fieldname() in Article.get_custom_fields()])
        if cls.have_category():
            fields.append('categories')
        if cls.have_storage():
            fields.append('stockage_total')
            fields.append('available_total')
        return fields

    @classmethod
    def get_edit_fields(cls):
        fields_desc = ["reference", "designation", ("price", ), ("unit", "qtyDecimal"), ("stockable", "isdisabled")]
        if cls.have_vat():
            fields_desc.extend([('vat', )])
        fields_desc.extend([('accountposting', )])
        fields = {_('001@Description'): fields_desc}
        if cls.have_category():
            fields[_('002@Extra')] = ['categories']
        return fields

    @classmethod
    def get_show_fields(cls):
        fields = {'': ["reference"]}
        fields_desc = ["designation", ("price", ), ("unit", "qtyDecimal"), ("stockable", "isdisabled")]
        if cls.have_vat():
            fields_desc.extend([('vat', )])
        fields_desc.extend([('accountposting', )])
        fields_desc.extend(cls.get_fields_to_show())
        if cls.have_category():
            fields_desc.append(('categories',))
        fields[_('001@Description')] = fields_desc
        if cls.have_provider():
            fields[_('002@Provider')] = ['provider_set']
        return fields

    @classmethod
    def get_search_fields(cls):
        fields = ["reference", "designation", "price", "unit", "qtyDecimal", "stockable"]
        if cls.have_vat():
            fields.append('vat')
        fields.extend(["isdisabled", "accountposting"])
        for cf_name, cf_model in CustomField.get_fields(cls):
            fields.append((cf_name, cf_model.get_field(), 'articlecustomfield__value', Q(articlecustomfield__field__id=cf_model.id)))
        if cls.have_category():
            fields.append('categories')
            fields.append('categories.name')
            fields.append('categories.designation')
        if cls.have_provider():
            fields.append('provider_set.third')
            fields.append('provider_set.reference')
        fields.append('storagedetail_set.storagesheet.storagearea')
        return fields

    @classmethod
    def get_print_fields(cls):
        fields = super(Article, cls).get_print_fields()
        if MultiPrice.objects.count() > 0:
            price_index = fields.index("price")
            fields.insert(price_index + 1, "current_price_txt")
        return fields

    @classmethod
    def get_import_fields(cls):
        fields = ["reference", "designation", "price"]
        for multi_price in MultiPrice.objects.all():
            fields.append((multi_price.get_fieldname(), multi_price.name))
        fields.extend(["unit", "accountposting", 'vat', "stockable", "isdisabled", "qtyDecimal"])
        if cls.have_category():
            fields.append('categories')
        if cls.have_provider():
            fields.append(('provider.third.contact', _('provider')))
            fields.append('provider.reference')
        for cf_field in CustomField.get_fields(cls):
            fields.append((cf_field[0], cf_field[1].name))
        return fields

    @classmethod
    def import_data(cls, rowdata, dateformat):
        try:
            new_item = super(Article, cls).import_data(rowdata, dateformat)
            if new_item is not None:
                new_item.set_custom_values(rowdata)
                if ('categories' in rowdata.keys()) and (rowdata['categories'] is not None) and (rowdata['categories'].strip() != ''):
                    cat = Category.objects.filter(name__iexact=rowdata['categories'].strip()).distinct()
                    if len(cat) > 0:
                        cat_ids = [cat[0].id]
                        for cat_item in new_item.categories.all():
                            cat_ids.append(cat_item.id)
                        new_item.categories.set(Category.objects.filter(id__in=cat_ids).distinct())
                        new_item.save()
                    else:
                        cls.import_logs.append(_("Category '%s' unknown !"))
                if ('provider.third.contact' in rowdata.keys()) and (rowdata['provider.third.contact'] is not None) and (rowdata['provider.third.contact'].strip() != ''):
                    if ('provider.reference' in rowdata.keys()) and (rowdata['provider.reference'] is not None):
                        reference = rowdata['provider.reference']
                    else:
                        reference = ''
                    q_legalentity = Q(contact__legalentity__name__iexact=rowdata['provider.third.contact'].strip())
                    q_individual = Q(completename__icontains=rowdata['provider.third.contact'])
                    thirds = Third.objects.annotate(completename=Concat('contact__individual__lastname', Value(' '),
                                                                        'contact__individual__firstname')).filter(q_legalentity | q_individual).distinct()
                    if len(thirds) > 0:
                        Provider.objects.get_or_create(article=new_item, third=thirds[0], reference=reference)
                    else:
                        cls.import_logs.append(_("Provider '%s' unknown !") % rowdata['provider.third.contact'].strip())
            return new_item
        except ValidationError:
            getLogger('diacamma.invoice').exception("import_data")
            raise LucteriosException(GRAVE, "Data error in this line:<br/> %s" % "<br/>".join(get_obj_contains(new_item)))
        except Exception:
            getLogger('diacamma.invoice').exception("import_data")
            raise

    @property
    def image(self):
        img_path = get_user_path("invoice", "Article_%s.jpg" % self.id)
        if exists(img_path):
            img = readimage_to_base64(img_path)
        else:
            img = readimage_to_base64(join(dirname(__file__), "static", 'diacamma.invoice', "images", "NoArticle.png"))
        return img.decode('ascii')

    @property
    def ref_price(self):
        return "%s [%s]" % (self.reference, get_amount_from_format_devise(self.price, 7))

    def get_designation(self):
        val = self.designation
        if Params.getvalue('invoice-custom-field-in-bill'):
            for cf_name, cf_model in CustomField.get_fields(self.__class__):
                val += "{[br/]} - {[u]}%s{[/u]}: {[i]}%s{[/i]}" % (cf_model.name, getattr(self, cf_name))
        return val

    def get_amount_from_area(self, currentqty, area):
        sum_amount = 0.0
        if self.id is not None:
            if self.stockable == self.STOCKABLE_KIT:
                for kitart in self.kit_article_set.all():
                    sum_amount += kitart.link_article.get_amount_from_area(currentqty * float(kitart.quantity), area)
            else:
                nb_qty = 0.0
                for det_item in self.storagedetail_set.filter(storagesheet__status=StorageSheet.STATUS_VALID,
                                                              storagesheet__sheet_type=StorageSheet.TYPE_RECEIPT,
                                                              storagesheet__storagearea_id=area).order_by('-storagesheet__date'):
                    if (nb_qty + float(det_item.quantity)) < currentqty:
                        sum_amount += float(det_item.price * det_item.quantity)
                        nb_qty += float(det_item.quantity)
                    else:
                        sum_amount += float(det_item.price) * (float(currentqty) - nb_qty)
                        break
        return sum_amount

    def get_stockage_values(self):
        if not hasattr(self, '_stock_list'):
            self._stock_list = []
            stock = {}
            if self.stockable in (self.STOCKABLE_YES, self.STOCKABLE_YES_WITHOUTSELL):
                detail_filter = Q(storagesheet__status=StorageSheet.STATUS_VALID)
                if self.show_storagearea != StorageArea.NO_AREA:
                    detail_filter &= Q(storagesheet__storagearea=self.show_storagearea)
                for val in self.storagedetail_set.filter(detail_filter).values('storagesheet__storagearea').annotate(data_sum=Sum('quantity')):
                    if abs(val['data_sum']) > 0.001:
                        if val['storagesheet__storagearea'] not in stock.keys():
                            stock[val['storagesheet__storagearea']] = [str(StorageArea.get_cache_text(val['storagesheet__storagearea'])), 0.0]
                        stock[val['storagesheet__storagearea']][1] += float(val['data_sum'])
            if self.stockable == self.STOCKABLE_KIT:
                for kitart in self.kit_article_set.all():
                    for areaid, area, qty, total_amount in kitart.link_article.get_stockage_values():
                        if areaid == StorageArea.NO_AREA:
                            continue
                        if areaid not in stock.keys():
                            stock[areaid] = [area, {}]
                        stock[areaid][1][kitart.id] = round(qty / float(kitart.quantity), self.qtyDecimal)
                for key in sorted(list(stock.keys())):
                    stock[key][1] = min(stock[key][1].values())
            if self.stockable != self.STOCKABLE_NO:
                total_amount = 0.0
                total_qty = 0.0
                for key in sorted(list(stock.keys())):
                    sum_amount = self.get_amount_from_area(stock[key][1], key)
                    self._stock_list.append((int(key), stock[key][0], stock[key][1], sum_amount))
                    total_qty += stock[key][1]
                    total_amount += sum_amount
                self._stock_list.append((0, _('Total'), total_qty, total_amount))
        return self._stock_list

    def get_booking_values(self):
        if not hasattr(self, '_booking_list'):
            self._booking_list = []
            booking = {}
            if self.stockable in (self.STOCKABLE_YES, self.STOCKABLE_YES_WITHOUTSELL):
                detail_filter = Q(bill__status=Bill.STATUS_VALID) & Q(bill__bill_type__in=(Bill.BILLTYPE_QUOTATION, Bill.BILLTYPE_CART, Bill.BILLTYPE_ORDER))
                if self.show_storagearea != StorageArea.NO_AREA:
                    detail_filter &= Q(storagearea=self.show_storagearea)
                for val in Detail.objects.filter(detail_filter).values('storagearea', 'article').annotate(data_sum=Sum('quantity')):
                    katart = RecipeKitArticle.objects.filter(link_article=self, article_id=val['article']).first()
                    if (val['article'] != self.id) and (katart is None):
                        continue
                    if (abs(val['data_sum']) > 0.001) and (val['storagearea'] is not None):
                        if not val['storagearea'] in booking.keys():
                            booking[val['storagearea']] = [str(StorageArea.get_cache_text(val['storagearea'])), 0.0]
                        booking[val['storagearea']][1] += float(val['data_sum']) * (1 if katart is None else float(katart.quantity))
            if self.stockable == self.STOCKABLE_KIT:
                for kitart in self.kit_article_set.all():
                    for areaid, area, qty in kitart.link_article.get_booking_values():
                        if areaid == StorageArea.NO_AREA:
                            continue
                        if areaid not in booking.keys():
                            booking[areaid] = [area, {}]
                        booking[areaid][1][kitart.id] = round(qty / float(kitart.quantity), self.qtyDecimal)
                for key in sorted(list(booking.keys())):
                    booking[key][1] = min(booking[key][1].values())
            if self.stockable != self.STOCKABLE_NO:
                total_qty = 0.0
                for key in sorted(list(booking.keys())):
                    self._booking_list.append((int(key), booking[key][0], booking[key][1]))
                    total_qty += booking[key][1]
                self._booking_list.append((0, _('Total'), total_qty))
        return self._booking_list

    def has_sufficiently(self, storagearea_id, quantity):
        if self.stockable != self.STOCKABLE_NO:
            available_qty = self.get_available_total_num(storagearea_id, 0)
            if (float(quantity) - available_qty) < 0.001:
                return True
            return False
        return True

    def get_stockage_total_num(self, storagearea=0, default=None):
        for val in self.get_stockage_values():
            if val[0] == storagearea:
                return float(val[2])
        return default

    def get_booking_total_num(self, storagearea=0, default=None):
        for val in self.get_booking_values():
            if val[0] == storagearea:
                return float(val[2])
        return default

    def get_available_total_num(self, storagearea=0, default=None):
        if self.stockable == self.STOCKABLE_KIT:
            if storagearea == 0:
                return sum([self.get_available_total_num(storagearea.id, default) for storagearea in StorageArea.objects.all()])
            else:
                available_list = []
                for kitart in self.kit_article_set.all():
                    stockage = kitart.link_article.get_stockage_total_num(storagearea=storagearea, default=0)
                    booking = kitart.link_article.get_booking_total_num(storagearea=storagearea, default=0)
                    available_list.append(round((stockage - booking) / float(kitart.quantity), self.qtyDecimal))
                if len(available_list) == 0:
                    return default
                elif len(available_list) == 1:
                    return available_list[0]
                else:
                    return min(available_list)
        elif self.stockable != self.STOCKABLE_NO:
            stockage = self.get_stockage_total_num(storagearea=storagearea, default=0)
            booking = self.get_booking_total_num(storagearea=storagearea, default=0)
            return stockage - booking
        return default

    def get_stockage_mean_price(self, storagearea=0):
        for val in self.get_stockage_values():
            if val[0] == storagearea:
                if abs(float(val[2])) > 0.0001:
                    return float(val[3]) / float(val[2])
                else:
                    break
        if self.stockable != self.STOCKABLE_NO:
            detail_filter = Q(storagesheet__status=StorageSheet.STATUS_VALID) & Q(storagesheet__sheet_type=StorageSheet.TYPE_RECEIPT)
            storage_detail = self.storagedetail_set.filter(detail_filter).order_by('-storagesheet__date').first()
            if storage_detail is not None:
                return storage_detail.price
        return 0.0

    def get_stockage_total(self):
        value = self.get_stockage_total_num()
        if value is not None:
            format_txt = "N%d" % int(self.qtyDecimal)
            return format_to_string(value, format_txt, None)
        return None

    def get_booking_total(self):
        value = self.get_booking_total_num()
        if value is not None:
            format_txt = "N%d" % int(self.qtyDecimal)
            return format_to_string(value, format_txt, None)
        return None

    def get_available_total(self):
        value = self.get_available_total_num()
        if value is not None:
            format_txt = "N%d" % int(self.qtyDecimal)
            return format_to_string(value, format_txt, None)
        return None

    def get_last_buy_price(self):
        last_buy = self.storagedetail_set.filter(storagesheet__status=StorageSheet.STATUS_VALID, storagesheet__sheet_type=StorageSheet.TYPE_RECEIPT).order_by('storagesheet__date').last()
        if last_buy is not None:
            return last_buy.price
        return None

    def get_mean_buy_price(self):
        if self.get_available_total_num(0, 0) > 0:
            return self.get_stockage_mean_price(0)
        return None

    def __getattr__(self, name):
        if name == "str":
            return str(self.get_final_child())
        if name[:len(MultiPrice.PREFIX_PRICE)] == MultiPrice.PREFIX_PRICE:
            if self.id is None:
                return 0
            else:
                multiprice_id = int(name[len(MultiPrice.PREFIX_PRICE):])
                multipricevalue = MultiPriceValue.objects.filter(article=self, multiprice_id=multiprice_id).first()
                return multipricevalue.price if multipricevalue is not None else self.price
        else:
            return CustomizeObject.__getattr__(self, name)

    def set_custom_values(self, params):
        CustomizeObject.set_custom_values(self, params)
        for multiprice in MultiPrice.objects.all():
            if multiprice.get_fieldname() in params.keys():
                multipricevalue = MultiPriceValue.objects.filter(article=self, multiprice=multiprice).first()
                if multipricevalue is not None:
                    multipricevalue.price = params[multiprice.get_fieldname()]
                    multipricevalue.save()
                else:
                    MultiPriceValue.objects.create(article=self, multiprice=multiprice, price=params[multiprice.get_fieldname()])

    def get_price_from_third(self, third_id):
        mutli_prices = [self.price]
        for multiprice in MultiPrice.objects.all():
            if multiprice.check_filtercriteria(third_id):
                mutli_prices.append(getattr(self, multiprice.get_fieldname()))
        return min(mutli_prices)

    def get_current_price(self):
        if self.current_third is not None:
            return self.get_price_from_third(self.current_third.id)
        else:
            return self.price

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        unicity_query = Q(reference=self.reference)
        if self.id is not None:
            unicity_query &= ~Q(id=self.id)
        if (Article.objects.filter(unicity_query).count() != 0):
            raise LucteriosException(IMPORTANT, _("article reference is not unique !"))
        return LucteriosModel.save(self, force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    class Meta(object):
        verbose_name = _('article')
        verbose_name_plural = _('articles')
        ordering = ['reference']


class RecipeKitArticle(LucteriosModel):
    article = models.ForeignKey(Article, verbose_name=_('own article'), related_name='kit_article', null=False, on_delete=models.CASCADE)
    link_article = models.ForeignKey(Article, verbose_name=_('linked article'), related_name='linked_article', null=False, on_delete=models.PROTECT)
    quantity = LucteriosDecimalField(verbose_name=_('amount in the recipe'), max_digits=12, decimal_places=3,
                                     default=1.0, validators=[MinValueValidator(0.0), MaxValueValidator(9999999.999)], format_string="N3")

    quantity_txt = LucteriosVirtualField(verbose_name=_('amount in the recipe'), compute_from="get_quantity_txt")
    link_article_fake = LucteriosVirtualField(verbose_name=_('linked article'), compute_from=lambda _this: "link article fake")

    def __init__(self, *args, **kwargs):
        LucteriosModel.__init__(self, *args, **kwargs)
        self.filter_ref = ''

    def set_context(self, xfer):
        self.filter_thirdid = xfer.getparam('third', 0)
        self.filter_ref = xfer.getparam('reference', '')
        self.filter_cat = xfer.getparam('cat_filter', ())
        self.filter_lib = xfer.getparam('ref_filter', '')

    def __str__(self):
        return "%d x %s" % (self.quantity, self.link_article)

    @classmethod
    def get_default_fields(cls):
        return ["link_article", "link_article.designation", "link_article.available_total", "quantity_txt"]

    @classmethod
    def get_edit_fields(cls):
        return ["article", "link_article_fake", "quantity"]

    def get_quantity_txt(self):
        return format_value(self.quantity, "N%d" % self.link_article.qtyDecimal)

    @property
    def link_article_query(self):
        artfilter = Q(isdisabled=False) & Q(stockable=Article.STOCKABLE_YES)
        artidexclude = [kitart.link_article.id for kitart in self.article.kit_article_set.exclude(id=self.id)]
        if self.filter_thirdid != 0:
            artfilter &= Q(provider__third_id=self.filter_thirdid)
        if self.filter_ref != '':
            artfilter &= Q(provider__reference__icontains=self.filter_ref)
        if self.filter_lib != '':
            artfilter &= Q(reference__icontains=self.filter_lib) | Q(designation__icontains=self.filter_lib)
        items = Article.objects.filter(artfilter).exclude(id__in=artidexclude).distinct()
        if len(self.filter_cat) > 0:
            for cat_item in Category.objects.filter(id__in=self.filter_cat).distinct():
                items = items.filter(categories__in=[cat_item]).distinct()
        return items

    class Meta(object):
        verbose_name = _('article of kit')
        verbose_name_plural = _('articles of kit')
        ordering = ['article', '-quantity']
        default_permissions = []


class Provider(LucteriosModel):
    article = models.ForeignKey(Article, verbose_name=_('article'), null=False, on_delete=models.CASCADE)
    third = models.ForeignKey(Third, verbose_name=_('third'), null=False, on_delete=models.PROTECT)
    reference = models.CharField(_('ref. provider'), max_length=50)

    @property
    def third_query(self):
        thirdfilter = Q(accountthird__code__regex=current_system_account().get_provider_mask())
        return Third.objects.filter(thirdfilter).distinct()

    def __str__(self):
        return self.reference

    @classmethod
    def get_default_fields(cls):
        return ["third", "reference"]

    @classmethod
    def get_edit_fields(cls):
        return ["third", "reference"]

    @classmethod
    def get_show_fields(cls):
        return ["third", "reference"]

    class Meta(object):
        verbose_name = _('Provider')
        verbose_name_plural = _('Providers')
        default_permissions = []


class CategoryBill(LucteriosModel):
    WORKFLOWS_BOTH = 0
    WORKFLOWS_ALWAYS_ORDER = 1
    WORKFLOWS_NEVER_ORDER = 2
    LIST_WORKFLOWS = ((WORKFLOWS_BOTH, _('on choice')), (WORKFLOWS_ALWAYS_ORDER, _('always order')), (WORKFLOWS_NEVER_ORDER, _('never order')))

    name = models.CharField(_('name'), max_length=100)
    designation = models.TextField(_('designation'))
    titles = models.TextField(_('titles'))

    printmodel = models.ForeignKey(PrintModel, verbose_name=_('print patern pre-sale'), related_name='categorybill_presale',
                                   null=True, default=None, db_index=True, on_delete=models.SET_NULL)
    printmodel_sold = models.ForeignKey(PrintModel, verbose_name=_('print patern sold'), related_name='categorybill_sold',
                                        null=True, default=None, db_index=True, on_delete=models.SET_NULL)
    emailsubject = models.CharField(_('email subject'), max_length=100)
    emailmessage = models.TextField(_('email message'))
    is_default = models.BooleanField(verbose_name=_('default'), default=False)
    special_numbering = models.BooleanField(verbose_name=_('special_numbering'), default=False)
    prefix_numbering = models.CharField(_('prefix numbering'), max_length=20, blank=True)
    workflow_order = models.IntegerField(verbose_name=_('workflow_order'), choices=LIST_WORKFLOWS, null=False, default=WORKFLOWS_BOTH, db_index=True)
    payment_method = models.ManyToManyField(PaymentMethod, verbose_name=_('payment method'), blank=True)
    with_multi_emailinfo = models.BooleanField(verbose_name=_('with multi emailinfo'), default=False)
    multi_emailinfo = models.TextField(_('multi emailinfo'), default='')

    titles_txt = LucteriosVirtualField(verbose_name=_('titles'), compute_from='get_titles_txt')

    def __str__(self):
        return str(self.name)

    @classmethod
    def get_default_fields(cls):
        return ["name", "designation", "titles_txt", "is_default"]

    @classmethod
    def get_edit_fields(cls):
        fields = ["name", "designation", ('special_numbering', 'prefix_numbering')]
        if Params.getvalue('invoice-order-mode') != Bill.INVOICE_ORDER_NONE:
            fields.append('workflow_order')
        fields.extend(['payment_method', ('printmodel', 'printmodel_sold'), 'with_multi_emailinfo', 'emailsubject', 'emailmessage', ])
        return fields

    @classmethod
    def get_show_fields(cls):
        fields = ["name", "designation", ('special_numbering', 'prefix_numbering')]
        if Params.getvalue('invoice-order-mode') != Bill.INVOICE_ORDER_NONE:
            fields.append('workflow_order')
        fields.extend([('printmodel', 'printmodel_sold'), 'payment_method', 'emailsubject', 'emailmessage'])
        return fields

    def change_has_default(self):
        all_cat = CategoryBill.objects.exclude(id=self.id)
        for cat_item in all_cat:
            cat_item.is_default = False
            cat_item.save()
        self.is_default = not self.is_default
        self.save()

    @property
    def printmodel_query(self):
        return PrintModel.objects.filter(kind=PrintModel.KIND_REPORT, modelname=Bill.get_long_name())

    @property
    def printmodel_sold_query(self):
        return self.printmodel_query

    def fill_default(self):
        if self.emailsubject == '':
            self.emailsubject = Params.getvalue('payoff-email-subject')
        if self.emailmessage == '':
            self.emailmessage = Params.getvalue('payoff-email-message')
        if self.titles == '':
            self.titles = dumps({item[0]: str(item[1]) for item in Bill.LIST_BILLTYPES})

    def get_title(self, type_num):
        try:
            titles = loads(self.titles)
        except JSONDecodeError:
            titles = {}
        if str(type_num) in titles:
            return titles[str(type_num)]
        else:
            return dict(Bill.LIST_BILLTYPES)[type_num]

    def set_title(self, type_num, newtitle):
        try:
            titles = loads(self.titles)
        except JSONDecodeError:
            titles = {}
        titles[type_num] = newtitle
        self.titles = dumps(titles)

    def get_multi_emailsubject(self, type_num):
        try:
            multi_emailinfo = loads(self.multi_emailinfo)
        except JSONDecodeError:
            multi_emailinfo = {}
        if (str(type_num) in multi_emailinfo) and ('subject' in multi_emailinfo[str(type_num)]):
            return multi_emailinfo[str(type_num)]['subject']
        else:
            return self.emailsubject

    def set_multi_emailsubject(self, type_num, emailsubject):
        try:
            multi_emailinfo = loads(self.multi_emailinfo)
        except JSONDecodeError:
            multi_emailinfo = {}
        if str(type_num) not in multi_emailinfo:
            multi_emailinfo[str(type_num)] = {}
        multi_emailinfo[str(type_num)]['subject'] = emailsubject
        self.multi_emailinfo = dumps(multi_emailinfo)

    def get_multi_emailmessage(self, type_num):
        try:
            multi_emailinfo = loads(self.multi_emailinfo)
        except JSONDecodeError:
            multi_emailinfo = {}
        if (str(type_num) in multi_emailinfo) and ('message' in multi_emailinfo[str(type_num)]):
            return multi_emailinfo[str(type_num)]['message']
        else:
            return self.emailmessage

    def set_multi_emailmessage(self, type_num, emailmessage):
        try:
            multi_emailinfo = loads(self.multi_emailinfo)
        except JSONDecodeError:
            multi_emailinfo = {}
        if str(type_num) not in multi_emailinfo:
            multi_emailinfo[str(type_num)] = {}
        multi_emailinfo[str(type_num)]['message'] = emailmessage
        self.multi_emailinfo = dumps(multi_emailinfo)

    def get_title_info(self):
        list_types = [type_item for type_item in Bill.LIST_BILLTYPES if (type_item[0] != Bill.BILLTYPE_RECEIPT) and ((Params.getvalue('invoice-cart-active') and self.is_default) or (type_item[0] != Bill.BILLTYPE_CART))]
        if (Params.getvalue('invoice-order-mode') == Bill.INVOICE_ORDER_NONE) or (self.workflow_order == self.WORKFLOWS_NEVER_ORDER):
            list_types = [type_item for type_item in list_types if type_item[0] != Bill.BILLTYPE_ORDER]
        for type_num, type_title in list_types:
            yield type_num, type_title, self.get_title(type_num)

    def get_titles_txt(self):
        result = []
        for _num, type_title, type_value in self.get_title_info():
            result.append("%s = %s" % (_("title of '%s'") % type_title, type_value))
        return result

    class Meta(object):
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        default_permissions = []


class Bill(Supporting):
    BILLTYPE_ALL = -1
    BILLTYPE_QUOTATION = 0
    BILLTYPE_BILL = 1
    BILLTYPE_ASSET = 2
    BILLTYPE_RECEIPT = 3
    BILLTYPE_ORDER = 4
    BILLTYPE_CART = 5
    LIST_BILLTYPES = ((BILLTYPE_CART, _('cart')), (BILLTYPE_QUOTATION, _('quotation')), (BILLTYPE_ORDER, _('order')), (BILLTYPE_BILL, _('bill')), (BILLTYPE_ASSET, _('asset')), (BILLTYPE_RECEIPT, _('receipt')))
    SELECTION_BILLTYPES = ((BILLTYPE_ALL, None),) + LIST_BILLTYPES

    STATUS_ALL = -2
    STATUS_BUILDING_VALID = -1
    STATUS_BUILDING = 0
    STATUS_VALID = 1
    STATUS_CANCEL = 2
    STATUS_ARCHIVE = 3
    LIST_STATUS = ((STATUS_BUILDING, _('building')), (STATUS_VALID, _('valid')), (STATUS_CANCEL, _('cancel')), (STATUS_ARCHIVE, _('archive')))
    SELECTION_STATUS = ((STATUS_BUILDING_VALID, '%s+%s' % (_('building'), _('valid'))),) + LIST_STATUS + ((STATUS_ALL, None),)

    INVOICE_ORDER_NONE = 0
    INVOICE_ORDER_CONVERT = 1
    INVOICE_ORDER_LINK = 2

    fiscal_year = models.ForeignKey(FiscalYear, verbose_name=_('fiscal year'), null=True, default=None, db_index=True, on_delete=models.CASCADE)
    bill_type = models.IntegerField(verbose_name=_('bill type'), choices=LIST_BILLTYPES, null=False, default=BILLTYPE_QUOTATION, db_index=True)
    num = models.IntegerField(verbose_name=_('numeros'), null=True)
    date = models.DateField(verbose_name=_('date'), null=False)
    comment = models.TextField(_('comment'), blank=True, default="")
    status = FSMIntegerField(verbose_name=_('status'), choices=LIST_STATUS, null=False, default=STATUS_BUILDING, db_index=True)
    entry = models.ForeignKey(EntryAccount, verbose_name=_('entry'), null=True, default=None, db_index=True, on_delete=models.PROTECT)
    cost_accounting = models.ForeignKey(CostAccounting, verbose_name=_('cost accounting'), null=True, default=None, db_index=True, on_delete=models.PROTECT)
    parentbill = models.ForeignKey("invoice.Bill", verbose_name=_('parent'), null=True, default=None, on_delete=models.SET_NULL)
    categoryBill = models.ForeignKey(CategoryBill, verbose_name=_('category'), null=True, default=None, on_delete=models.SET_NULL)

    total = LucteriosVirtualField(verbose_name=_('total'), compute_from='get_total_ex', format_string=lambda: format_with_devise(5))
    num_txt = LucteriosVirtualField(verbose_name=_('numeros'), compute_from='get_num_txt')
    total_excltax = LucteriosVirtualField(verbose_name=_('total'), compute_from='get_total_excltax', format_string=lambda: format_with_devise(5))
    vta_sum = LucteriosVirtualField(verbose_name=_('VTA sum'), compute_from='get_vta_sum', format_string=lambda: format_with_devise(5))
    total_incltax = LucteriosVirtualField(verbose_name=_('total incl. taxes'), compute_from='get_total_incltax', format_string=lambda: format_with_devise(5))

    title_vta_details = LucteriosVirtualField(verbose_name='', compute_from='get_title_vta_details')
    vta_details = LucteriosVirtualField(verbose_name='', compute_from='get_vta_details', format_string=lambda: format_with_devise(5))

    origin = LucteriosVirtualField(verbose_name=_('origin'), compute_from='get_origin')
    description = LucteriosVirtualField(verbose_name='', compute_from='get_description')

    billtype = LucteriosVirtualField(verbose_name=_('type title'), compute_from='get_billtype')

    def __str__(self):
        if self.num is None:
            return "%s - %s" % (self.billtype, get_date_formating(self.date))
        else:
            return "%s %s - %s" % (self.billtype, self.num_txt, get_date_formating(self.date))

    @property
    def reference(self):
        billtype = self.billtype
        billtype = billtype[0].upper() + billtype[1:].lower()
        if self.num is None:
            return "%s" % billtype
        else:
            return "%s %s" % (billtype, self.num_txt)

    @classmethod
    def get_default_fields(cls, status=-1):
        fields = ["bill_type", "num_txt", "date", "third", "comment", 'total']
        if status < 0:
            fields.append("status")
        elif status == 1:
            fields.append(Supporting.get_payoff_fields()[-1][-1])
        if CategoryBill.objects.count() > 0:
            fields.insert(1, 'billtype')
        return fields

    @classmethod
    def get_payment_fields(cls):
        return ["third", ("billtype", "num_txt",), ("date", 'total',)]

    def get_third_mask(self):
        return current_system_account().get_customer_mask()

    @classmethod
    def get_edit_fields(cls):
        fields = ["bill_type", "date", "comment"]
        if CategoryBill.objects.count() > 0:
            fields.insert(0, 'categoryBill')
        return fields

    @classmethod
    def get_search_fields(cls):
        search_fields = ["bill_type", "fiscal_year", "num", "date", "comment", "status"]
        for fieldname in Third.get_search_fields(with_addon=False):
            search_fields.append(cls.convert_field_for_search("third", fieldname))
        for fieldname in Detail.get_search_fields():
            search_fields.append(cls.convert_field_for_search("detail_set", fieldname))
        for fieldname in Payoff.get_search_fields():
            search_fields.append(cls.convert_field_for_search("payoff_set", fieldname))
        return search_fields

    @classmethod
    def get_show_fields(cls):
        fields = [("num_txt", "date"), "third", "detail_set", "comment", ("status", 'total_excltax')]
        if CategoryBill.objects.count() > 0:
            fields.append(('categoryBill', "bill_type"))
        return fields

    @classmethod
    def get_print_fields(cls):
        print_fields = [(_("bill type"), "type_bill"), "num_txt", "date", "third", "detail_set"]
        print_fields.extend(Supporting.get_print_fields())
        print_fields.extend(["comment", "status", 'total_excltax', 'vta_sum', 'total_incltax', 'origin'])
        print_fields.append('OUR_DETAIL')
        print_fields.append('DEFAULT_DOCUMENTS')
        return print_fields

    @property
    def bill_type_list(self):
        if self.categoryBill_id is None:
            return Bill.LIST_BILLTYPES
        else:
            return [(info[0], info[2])for info in self.categoryBill.get_title_info()]

    def get_billtype(self):
        if self.categoryBill_id is None:
            return get_value_if_choices(self.bill_type, self.get_field_by_name("bill_type"))
        else:
            return self.categoryBill.get_title(self.bill_type)

    @property
    def type_bill(self):
        return self.get_billtype().upper()

    def get_total_ex(self):
        if Params.getvalue("invoice-vat-mode") == Vat.MODE_PRICEWITHVAT:
            return self.get_total_incltax()
        else:
            return self.get_total_excltax()

    def get_current_date(self):
        return self.date

    def get_third_masks_by_amount(self, amount):
        if self.bill_type == 0:
            return []
        else:
            masks = {}
            total = self.get_total()
            for detail in self.detail_set.all():
                mask = self.get_third_mask()
                if (detail.article_id is not None) and (detail.article.accountposting is not None) and (detail.article.accountposting.provision_third_account != ''):
                    mask = correct_accounting_code(detail.article.accountposting.provision_third_account)
                    AccountThird.objects.get_or_create(third=self.third, code=mask)
                if mask not in masks:
                    masks[mask] = 0
                masks[mask] += detail.get_total() * amount / total
            if len(masks) == 1 and (self.get_third_mask() in masks):
                return Supporting.get_third_masks_by_amount(self, amount)
            else:
                return list(masks.items())

    def get_min_payoff(self, ignore_payoff=-1):
        min_payoff = min(0, self.get_total_rest_topay(ignore_payoff) * 1.5)
        if abs(min_payoff) < 0.00001:
            currency_decimal = Params.getvalue("accounting-devise-prec")
            min_payoff = 1 * 10 ** (-1 * currency_decimal)
        return min_payoff

    def get_max_payoff(self, ignore_payoff=-1):
        max_payoff = max(self.get_total_rest_topay(ignore_payoff) * 100, 0)
        if abs(max_payoff) < 0.00001:
            currency_decimal = Params.getvalue("accounting-devise-prec")
            max_payoff = -1 * 10 ** (-1 * currency_decimal)
        return max_payoff

    def get_total_excltax(self):
        val = 0
        if self.id is not None:
            for detail in self.detail_set.all():
                val += detail.get_total_excltax()
        return val

    def get_reduce_excltax(self):
        val = 0
        if self.id is not None:
            for detail in self.detail_set.all():
                val += detail.get_reduce_excltax()
        return val

    def get_vta_sum(self):
        val = 0
        if self.id is not None:
            for detail in self.detail_set.all():
                val += detail.get_vta()
        return val

    def get_tax_sum(self):
        return self.get_vta_sum()

    def get_total_incltax(self):
        val = 0
        if self.id is not None:
            for detail in self.detail_set.all():
                val += detail.get_total_incltax()
        return val

    def get_total(self):
        return self.get_total_incltax()

    def get_num_txt(self):
        if (self.fiscal_year is None) or (self.num is None):
            return None
        elif (self.categoryBill is not None) and self.categoryBill.special_numbering and (self.categoryBill.prefix_numbering != ''):
            value = "%s-%s-%d" % (self.fiscal_year.prefix, self.categoryBill.prefix_numbering, self.num)
        else:
            value = "%s-%d" % (self.fiscal_year.prefix, self.num)
        return value

    def get_origin(self):
        if self.parentbill is not None:
            return _('origin : %s') % self.parentbill
        else:
            return ""

    def get_description(self):
        res = "{[table width='100%' border='1' style='border-collapse: collapse;']}\n"
        res += "{[tr]}{[th]}%s{[/th]}{[th]}%s{[/th]}{[th]}%s{[/th]}{[th]}%s{[/th]}{[th]}%s{[/th]}{[th]}%s{[/th]}{[/tr]}\n" % (_('designation'), _('price'), _('quantity'), _('unit'), _('reduce'), _('total'))
        if self.id is not None:
            for det in self.detail_set.all():
                res += "{[tr]}"
                res += "{[td]}%s{[/td]}" % det.designation
                res += "{[td]}%s{[/td]}" % get_amount_from_format_devise(det.price_txt, 5)
                res += "{[td]}%s{[/td]}" % round(det.quantity, det.article.qtyDecimal if det.article_id is not None else 3)
                res += "{[td]}%s{[/td]}" % det.unit
                res += "{[td]}%s{[/td]}" % (det.reduce_txt if det.reduce_txt is not None else '',)
                res += "{[td]}%s{[/td]}" % get_amount_from_format_devise(det.total, 5)
                res += "{[/tr]}\n"
        res += "{[/table]}\n"
        return res

    def get_vta_detail_list(self):
        vtas = {}
        if self.id is not None:
            for detail in self.detail_set.all():
                if abs(detail.vta_rate) > 0.001:
                    vta_txt = "%.2f" % abs(float(detail.vta_rate) * 100.0)
                    if vta_txt not in vtas.keys():
                        vtas[vta_txt] = float(0.0)
                    vtas[vta_txt] += detail.get_vta()
        return vtas

    def get_title_vta_details(self):
        vtas = []
        if self.id is not None:
            for vta in self.get_vta_detail_list().keys():
                vtas.append(_("VAT %s %%") % vta)
        return vtas

    def get_vta_details(self):
        return list(self.get_vta_detail_list().values())

    def payoff_is_revenu(self):
        return self.bill_type not in (self.BILLTYPE_QUOTATION, self.BILLTYPE_CART, self.BILLTYPE_ASSET)

    def entry_links(self):
        if self.entry_id is not None:
            return [self.entry]
        else:
            return []

    def get_default_costaccounting(self):
        detail_costlist = {}
        if self.id is not None:
            for detail in self.detail_set.all():
                if (detail.article is not None) and (detail.article.accountposting is not None):
                    detail_cost = detail.article.accountposting.cost_accounting
                    if detail_cost not in detail_costlist.keys():
                        detail_costlist[detail_cost] = 0
                    detail_costlist[detail_cost] += detail.get_total_excltax() + detail.get_reduce_excltax()
        default_cost = None
        last_total = 0
        for detail_cost, total in detail_costlist.items():
            if total > last_total:
                last_total = total
                default_cost = detail_cost
        return default_cost

    def get_warning_state(self):
        warning = []
        if self.bill_type in (self.BILLTYPE_QUOTATION, self.BILLTYPE_ORDER):
            for detail in self.detail_set.all():
                if (detail.article_id is not None) and not detail.article.has_sufficiently(detail.storagearea_id, detail.quantity):
                    if (detail.article.accountposting is not None) and (detail.article.accountposting.provision_third_account != ''):
                        warning.append(_("Article %s is not sufficiently stocked") % str(detail.article))
        if self.bill_type not in (self.BILLTYPE_QUOTATION, self.BILLTYPE_CART, self.BILLTYPE_ORDER):
            try:
                if len(self.check_date_year_valid(self.date)) == 0:
                    warning.extend(self.check_date_current_year(self.date.isoformat()))
            except LucteriosException:
                pass
        return warning

    def get_info_state(self):
        info = []
        if self.status == self.STATUS_BUILDING:
            info = Supporting.get_info_state(self, current_system_account().get_customer_mask())
        details = self.detail_set.all() if self.id is not None else []
        if len(details) == 0:
            info.append(str(_("no detail")))
        else:
            if self.bill_type != self.BILLTYPE_ASSET:
                for detail in details:
                    if (detail.article_id is not None) and not detail.article.has_sufficiently(detail.storagearea_id, detail.quantity):
                        if (detail.article.accountposting is None) or (detail.article.accountposting.provision_third_account == '') or (self.bill_type not in (self.BILLTYPE_QUOTATION, self.BILLTYPE_ORDER)):
                            info.append(_("Article %s is not sufficiently stocked") % str(detail.article))
            for detail in details:
                if detail.article is not None:
                    if detail.article.accountposting is None:
                        detail_code = ""
                    else:
                        detail_code = detail.article.accountposting.sell_account
                else:
                    detail_code = Params.getvalue("invoice-default-sell-account")
                detail_account = None
                if match(current_system_account().get_revenue_mask(), detail_code) is not None:
                    try:
                        detail_account = ChartsAccount.get_account(detail_code, FiscalYear.get_current())
                    except LucteriosException:
                        break
                if detail_account is None:
                    info.append(str(_("article has code account unknown!")))
                    break
        try:
            self.date = convert_date(self.date)
            info.extend(self.check_date_year_valid(self.date))
        except LucteriosException:
            pass
        return info

    def can_delete(self):
        if self.status != self.STATUS_BUILDING:
            return _('"%s" cannot be deleted!') % str(self)
        return ''

    def generate_storage(self):
        if self.bill_type == self.BILLTYPE_ASSET:
            sheet_type = StorageSheet.TYPE_RECEIPT
        else:
            sheet_type = StorageSheet.TYPE_EXIT
        old_area = 0
        last_sheet = None
        for detail in self.detail_set.filter(storagearea__isnull=False).order_by('storagearea'):
            if old_area != detail.storagearea_id:
                old_area = detail.storagearea_id
                if last_sheet is not None:
                    last_sheet.valid()
                last_sheet = StorageSheet.objects.create(sheet_type=sheet_type, storagearea_id=old_area, date=self.date, comment=str(self), status=0)
            if last_sheet is not None:
                if detail.article.stockable == Article.STOCKABLE_YES:
                    price = detail.article.get_stockage_mean_price() if (self.bill_type == self.BILLTYPE_ASSET) else 0.0
                    StorageDetail.objects.create(storagesheet=last_sheet, article=detail.article, quantity=abs(detail.quantity), price=price)
                elif detail.article.stockable == Article.STOCKABLE_KIT:
                    for kitart in detail.article.kit_article_set.all():
                        price = kitart.link_article.get_stockage_mean_price() if (self.bill_type == self.BILLTYPE_ASSET) else 0.0
                        StorageDetail.objects.create(storagesheet=last_sheet, article=kitart.link_article, quantity=abs(float(detail.quantity) * float(kitart.quantity)), price=price)
        if last_sheet is not None:
            last_sheet.valid()

    def _get_detail_for_entry(self):
        remise_account = None
        detail_list = {}
        if self.id is not None:
            for detail in self.detail_set.all():
                detail_cost = None
                if detail.article is not None:
                    if detail.article.accountposting is None:
                        detail_code = ""
                    else:
                        detail_code = detail.article.accountposting.sell_account
                        detail_cost = detail.article.accountposting.cost_accounting_id
                else:
                    detail_code = Params.getvalue("invoice-default-sell-account")
                    cost_account = CostAccounting.objects.filter(status=CostAccounting.STATUS_OPENED, is_default=True).first()
                    if cost_account is not None:
                        detail_cost = cost_account.id
                detail_account = ChartsAccount.get_account(detail_code, self.fiscal_year)
                if detail_account is None:
                    raise LucteriosException(IMPORTANT, _("article has code account unknown!"))
                if (detail_code, detail_cost) not in detail_list.keys():
                    detail_list[detail_code, detail_cost] = [detail_account, 0, detail_cost]
                detail_list[detail_code, detail_cost][1] += detail.get_total_excltax() + detail.get_reduce_excltax()
                if detail.get_reduce_excltax() > 0.001:
                    if remise_account is None:
                        remise_code = Params.getvalue("invoice-reduce-account")
                        remise_account = ChartsAccount.get_account(remise_code, self.fiscal_year)
                        if remise_account is None:
                            raise LucteriosException(IMPORTANT, _("reduce-account is not defined!"))
                    if (remise_code, detail_cost) not in detail_list.keys():
                        detail_list[remise_code, detail_cost] = [remise_account, 0, detail_cost]
                    detail_list[remise_code, detail_cost][1] -= detail.get_reduce_excltax()
        return detail_list

    def _compute_vat(self, is_bill):
        vat_val = {}
        if self.id is not None:
            for detail in self.detail_set.all():
                if (detail.article is not None) and (detail.article.vat is not None):
                    vataccount = detail.article.vat.account
                    if vataccount not in vat_val.keys():
                        vat_val[vataccount] = 0.0
                    vat_val[vataccount] += detail.get_vta()
        for vataccount, vatamount in vat_val.items():
            if vatamount > 0.001:
                vat_account = ChartsAccount.get_account(vataccount, self.fiscal_year)
                if vat_account is None:
                    raise LucteriosException(IMPORTANT, _("vta-account is not defined!"))
                EntryLineAccount.objects.create(account=vat_account, amount=is_bill * vatamount, entry=self.entry)

    def generate_entry(self):
        if self.bill_type == self.BILLTYPE_ASSET:
            is_bill = -1
        else:
            is_bill = 1
        third_account = self.get_third_account(current_system_account().get_customer_mask(), self.fiscal_year)
        self.entry = EntryAccount.objects.create(year=self.fiscal_year, date_value=self.date, designation=self.reference,
                                                 journal=Journal.objects.get(id=Journal.DEFAULT_SELLING))
        if abs(self.get_total_incltax()) > 0.0001:
            EntryLineAccount.objects.create(account=third_account, amount=is_bill * self.get_total_incltax(), third=self.third, entry=self.entry)
        detail_list = self._get_detail_for_entry()
        detail_keys = list(detail_list.keys())
        detail_keys.sort(key=lambda item: "%s__%s" % item)
        for detail_key in detail_keys:
            detail_item = detail_list[detail_key]
            if abs(detail_item[1]) > 0.0001:
                EntryLineAccount.objects.create(account=detail_item[0], amount=is_bill * detail_item[1], entry=self.entry, costaccounting_id=detail_item[2])
        if Params.getvalue("invoice-vat-mode") != Vat.MODE_NOVAT:
            self._compute_vat(is_bill)
        no_change, debit_rest, credit_rest = self.entry.serial_control(self.entry.get_serial())
        if not no_change and (len(self.entry.entrylineaccount_set.all()) == 0):
            entry_empty = self.entry
            self.entry = None
            entry_empty.delete()
        elif not no_change or (abs(debit_rest) > 0.001) or (abs(credit_rest) > 0.001):
            raise LucteriosException(GRAVE, _("Error in accounting generator!") + "{[br/]} no_change=%s debit_rest=%.3f credit_rest=%.3f" % (no_change, debit_rest, credit_rest))

    def _error_transaction(self, transation):
        return "%s: status=%d info_state = %s" % (transation, self.status, "\n".join(self.get_info_state()))

    def affect_num(self):
        if self.num is None:
            self.date = convert_date(self.date)
            info = self.check_date_year_valid(self.date)
            if len(info) == 1:
                raise LucteriosException(GRAVE, info[0])
            self.fiscal_year = FiscalYear.get_current(self.date)
            num_filter = Q(bill_type=self.bill_type) & Q(fiscal_year=self.fiscal_year)
            if (self.categoryBill is not None) and self.categoryBill.special_numbering:
                num_filter &= Q(categoryBill=self.categoryBill)
            bill_list = Bill.objects.filter(num_filter).exclude(status=0)
            val = bill_list.aggregate(Max('num'))
            if val['num__max'] is None:
                self.num = 1
            else:
                self.num = val['num__max'] + 1

    @property
    def associate_bill_asset(self):
        if (self.status in (Bill.STATUS_VALID, Bill.STATUS_ARCHIVE)) and (self.bill_type in (Bill.BILLTYPE_BILL, Bill.BILLTYPE_ASSET)) and \
                (abs(self.total_rest_topay) < 1e-3) and (self.payoff_set.count() == 1):
            payoff = self.payoff_set.first()
            if (payoff.mode == Payoff.MODE_INTERNAL) and (payoff.linked_payoff is not None):
                other_support = payoff.linked_payoff.supporting.get_final_child()
                if isinstance(other_support, Bill) and (other_support.status in (Bill.STATUS_VALID, Bill.STATUS_ARCHIVE)) and \
                        (other_support.bill_type in (Bill.BILLTYPE_BILL, Bill.BILLTYPE_ASSET)) and \
                        (abs(other_support.total_rest_topay) < 1e-3) and (other_support.payoff_set.count() == 1):
                    return other_support
        return None

    def adding_payoff(self, payoff):
        if payoff.mode == Payoff.MODE_INTERNAL:
            bill_asset = self.associate_bill_asset
            if (bill_asset is not None) and (bill_asset.status != self.status):
                if bill_asset.status == Bill.STATUS_VALID:
                    bill_asset.archive()
                elif self.status == Bill.STATUS_VALID:
                    self.archive()
        return

    def get_bcclist(self):
        if self.bill_type != self.BILLTYPE_CART:
            return Supporting.get_bcclist(self)
        bcclist = []
        for area in self.get_nb_area():
            if (area is not None) and (area.contact is not None):
                bcclist.extend(area.contact.email.replace(',', ';').split(";"))
        bcclist = list(set(bcclist))
        bcclist.sort()
        if '' in bcclist:
            bcclist.remove('')
        if len(bcclist) > 0:
            return bcclist
        return None

    def get_nb_area(self):
        area_set = set()
        if self.id is not None:
            for detail in self.detail_set.all():
                area_set.add(detail.storagearea)
        return area_set

    @classmethod
    def clean_timeout_cart(cls, third=None):
        timeout_days = Params.getvalue('invoice-cart-timeout')
        if timeout_days > 0:
            date_timeout = timezone.now().date() - timedelta(days=timeout_days)
            query_cart = Q(status=Bill.STATUS_BUILDING) & Q(bill_type=Bill.BILLTYPE_CART) & Q(date__lte=date_timeout)
            if third is not None:
                query_cart &= Q(third=third)
            for bill_cart in Bill.objects.filter(query_cart):
                bill_cart.delete()

    def send_card_email(self):
        from diacamma.payoff.views import can_send_email

        def replace_tag(contact, text):
            text = text.replace('#name', contact.get_presentation() if contact is not None else '???')
            text = text.replace('#doc', str(self.get_docname()))
            text = text.replace('#reference', str(self.reference))
            text = text.replace('#nb', str(len(self.get_nb_area())))
            return text
        if (self.bill_type != self.BILLTYPE_CART) or not can_send_email(None):
            return
        subject = Params.getvalue('invoice-cart-email-subject')
        message = Params.getvalue('invoice-cart-email-body')
        contact = self.third.contact.get_final_child()
        html_message = "<html>"
        html_message += message.replace('{[newline]}', '<br/>\n').replace('{[', '<').replace(']}', '>')
        html_message += "</html>"
        self.send_email(replace_tag(contact, subject), replace_tag(contact, html_message), self.get_default_print_model())

    def send_email_by_type(self):
        def replace_tag(contact, text):
            text = text.replace('#name', contact.get_presentation() if contact is not None else '???')
            text = text.replace('#doc', str(self.get_docname()))
            text = text.replace('#reference', str(self.reference))
            return text
        subject = self.get_email_subject()
        message = self.get_email_message()
        contact = self.third.contact.get_final_child()
        html_message = "<html>"
        html_message += message.replace('{[newline]}', '<br/>\n').replace('{[', '<').replace(']}', '>')
        html_message += "</html>"
        self.send_email(replace_tag(contact, subject), replace_tag(contact, html_message), self.get_default_print_model())

    transitionname__valid = _("Validate")

    @transition(field=status, source=STATUS_BUILDING, target=None, conditions=[lambda item:item.get_info_state() == []])
    def valid(self):
        self.affect_num()
        self.status = self.STATUS_VALID
        if not (self.bill_type in (self.BILLTYPE_QUOTATION, self.BILLTYPE_CART, self.BILLTYPE_ORDER)):
            self.generate_entry()
            self.generate_storage()
        self.generate_pdfreport()
        self.save()
        Signal.call_signal("change_bill", 'valid', self, None)
        if self.bill_type == self.BILLTYPE_CART:
            self.send_card_email()
            self.convert_to_quotation()

    def generate_pdfreport(self):
        if (self.status not in (self.STATUS_BUILDING, self.STATUS_CANCEL)) and not (self.bill_type in (Bill.BILLTYPE_QUOTATION, self.BILLTYPE_CART, Bill.BILLTYPE_ORDER)):
            return Supporting.generate_pdfreport(self)
        return None

    def renew_generate_pdfreport(self):
        if self.status == self.STATUS_BUILDING:
            self.valid()
        else:
            Supporting.renew_generate_pdfreport(self)

    transitionname__archive = _("Archive")

    @transition(field=status, source=STATUS_VALID, target=STATUS_ARCHIVE)
    def archive(self):
        self.status = self.STATUS_ARCHIVE
        self.save()
        Signal.call_signal("change_bill", 'archive', self, None)
        bill_asset = self.associate_bill_asset
        if (bill_asset is not None) and (bill_asset.status == Bill.STATUS_VALID):
            bill_asset.archive()

    transitionname__unarchive = _("Unarchive")

    @transition(field=status, source=STATUS_ARCHIVE, target=STATUS_VALID)
    def unarchive(self):
        self.status = self.STATUS_VALID
        self.save()
        bill_asset = self.associate_bill_asset
        if (bill_asset is not None) and (bill_asset.status == Bill.STATUS_ARCHIVE):
            bill_asset.unarchive()

    def undo(self):
        new_undo = Bill.objects.create(bill_type=Bill.BILLTYPE_ASSET if self.bill_type != Bill.BILLTYPE_ASSET else Bill.BILLTYPE_BILL,
                                       date=timezone.now(),
                                       third=self.third,
                                       status=Bill.STATUS_BUILDING,
                                       categoryBill=self.categoryBill,
                                       parentbill=self)
        for detail in self.detail_set.all():
            detail.id = None
            detail.bill = new_undo
            detail.save()
        if Params.getvalue("invoice-asset-mode") == 0:
            self.status = Bill.STATUS_ARCHIVE
        self.save()
        Signal.call_signal("change_bill", 'cancel', self, new_undo)
        return new_undo.id

    transitionname__cancel = _("Cancel")

    @transition(field=status, source=STATUS_VALID, target=STATUS_CANCEL, conditions=[lambda item:item.bill_type in (Bill.BILLTYPE_CART, Bill.BILLTYPE_QUOTATION, Bill.BILLTYPE_ORDER)])
    def cancel(self):
        return None

    def generate_accountlink(self):
        nb_link_created = Supporting.generate_accountlink(self)
        if (abs(self.get_total_rest_topay()) < 0.0001) and (self.entry is not None) and (self.parentbill is not None) and (self.parentbill.bill_type == Bill.BILLTYPE_ORDER):
            for account in ChartsAccount.objects.filter(entrylineaccount__entry=self.entry, code__regex=self.get_third_mask()).distinct():
                if self.entry.entrylineaccount_set.filter(account=account, link__isnull=True) == 0:
                    break
                try:
                    entrylines_to_link = []
                    entrylines_to_link.extend(list(self.entry.entrylineaccount_set.filter(account=account)))
                    for payoff in self.payoff_set.all():
                        for third_line in payoff.entry.entrylineaccount_set.filter(account=account):
                            entrylines_to_link.append(third_line)
                    if self.parentbill is not None:
                        for payoff in self.parentbill.payoff_set.all():
                            for third_line in payoff.entry.entrylineaccount_set.filter(account=account):
                                entrylines_to_link.append(third_line)
                    if len(entrylines_to_link) > 0:
                        AccountLink.create_link(entrylines_to_link)
                    nb_link_created += 1
                except LucteriosException as err:
                    getLogger("diacamma.invoice").debug("Link failed for %s : %s", entrylines_to_link, err)
        return nb_link_created

    def convert_payoff(self, new_bill):
        serial_vals = []
        amount = 0.0
        third_account = self.get_third_account(current_system_account().get_customer_mask(), self.fiscal_year)
        for payoff in self.payoff_set.all():
            for third_line in payoff.entry.entrylineaccount_set.filter(account__code__regex=self.get_third_mask()):
                if third_line.account != third_account:
                    amount += third_line.amount
                    third_line.amount = -1 * third_line.amount
                    third_line.id = 0
                    serial_vals.append(third_line.get_serial())
        if len(serial_vals) > 0:
            serial_vals.append(EntryLineAccount.add_serial(third_account.id, amount if amount < -0.001 else 0, amount if amount > 0.001 else 0, self.third.id))
            new_entry = EntryAccount.objects.create(year=FiscalYear.get_current(new_bill.date), date_value=new_bill.date, designation=_('%s supply transfer') % self, journal=Journal.objects.get(id=Journal.DEFAULT_OTHER))
            serial_vals = "\n".join(serial_vals)
            _no_change, debit_rest, credit_rest = new_entry.serial_control(serial_vals)
            if abs(debit_rest - credit_rest) >= 0.001:
                raise LucteriosException(GRAVE, _("Account entry not balanced{[br/]}total credit=%(credit)s - total debit=%(debit)s%(info)s") % {'credit': get_amount_from_format_devise(debit_rest, 7),
                                                                                                                                                 'debit': get_amount_from_format_devise(credit_rest, 7),
                                                                                                                                                 'info': self})
            new_entry.save_entrylineaccounts(serial_vals)
            new_entry.save()
            Payoff.objects.create(supporting=new_bill, date=new_entry.date_value,
                                  amount=abs(sum([payoff.amount for payoff in self.payoff_set.all()])),
                                  mode=Payoff.MODE_INTERNAL, payer=str(self.third), reference=new_entry.designation, entry=new_entry, bank_account=None)
            for account in ChartsAccount.objects.filter(entrylineaccount__entry=new_entry, code__regex=self.get_third_mask()).distinct():
                try:
                    entrylines_to_link = []
                    for payoff in self.payoff_set.all():
                        for third_line in payoff.entry.entrylineaccount_set.filter(account=account):
                            entrylines_to_link.append(third_line)
                    entrylines_to_link.extend(list(new_entry.entrylineaccount_set.filter(account=account)))
                    if len(entrylines_to_link) > 0:
                        AccountLink.create_link(entrylines_to_link)
                except LucteriosException as err:
                    getLogger("diacamma.invoice").debug("Link failed for %s : %s", entrylines_to_link, err)
        else:
            for payoff in self.payoff_set.all():
                payoff.supporting = new_bill
                payoff.save(do_generate=False, do_linking=False, do_internal=False)

    def convert_to_bill(self, billdate=None, comment=None):
        if (self.status == Bill.STATUS_VALID) and (self.bill_type in (Bill.BILLTYPE_QUOTATION, Bill.BILLTYPE_ORDER)):
            self.status = Bill.STATUS_ARCHIVE
            self.save()
            new_type = Bill.BILLTYPE_BILL
            new_bill = Bill.objects.create(bill_type=new_type, date=timezone.now().date() if (billdate is None) else convert_date(billdate),
                                           third=self.third, status=Bill.STATUS_BUILDING, categoryBill=self.categoryBill,
                                           comment=self.comment if comment is None else comment, parentbill=self)
            for detail in self.detail_set.all():
                detail.id = None
                detail.bill = new_bill
                detail.save(check_autoreduce=False)
            self.convert_payoff(new_bill)
            Signal.call_signal("change_bill", 'convert', self, new_bill)
            return new_bill
        else:
            return None

    def convert_to_order(self, comment=None):
        if (self.status == Bill.STATUS_VALID) and (self.bill_type == Bill.BILLTYPE_QUOTATION):
            self.status = Bill.STATUS_ARCHIVE
            self.save()
            new_bill = Bill.objects.create(bill_type=Bill.BILLTYPE_ORDER, date=timezone.now(),
                                           third=self.third, status=Bill.STATUS_VALID, categoryBill=self.categoryBill,
                                           comment=self.comment if comment is None else comment, parentbill=self)
            new_bill.affect_num()
            new_bill.save()
            for detail in self.detail_set.all():
                detail.id = None
                detail.bill = new_bill
                detail.save(check_autoreduce=False)
            Signal.call_signal("change_bill", 'convert', self, new_bill)
            return new_bill
        else:
            return None

    def convert_to_quotation(self):
        if (self.status == Bill.STATUS_VALID) and (self.bill_type == Bill.BILLTYPE_CART):
            self.status = Bill.STATUS_ARCHIVE
            self.save()
            for area in self.get_nb_area():
                new_bill = Bill.objects.create(bill_type=Bill.BILLTYPE_QUOTATION, date=timezone.now(),
                                               third=self.third, status=Bill.STATUS_BUILDING, categoryBill=self.categoryBill,
                                               comment=self.comment, parentbill=self)
                new_bill.save()
                for detail in self.detail_set.filter(storagearea=area):
                    detail.id = None
                    detail.bill = new_bill
                    detail.save(check_autoreduce=False)
                Signal.call_signal("change_bill", 'convert', self, new_bill)
            return new_bill
        else:
            return None

    def clone_quotation(self):
        if (self.status in (Bill.STATUS_VALID, Bill.STATUS_CANCEL, Bill.STATUS_ARCHIVE)) and (self.bill_type == Bill.BILLTYPE_QUOTATION):
            new_bill = Bill.objects.create(bill_type=Bill.BILLTYPE_QUOTATION, date=timezone.now(),
                                           third=self.third, status=Bill.STATUS_BUILDING, categoryBill=self.categoryBill,
                                           comment=self.comment, parentbill=self)
            new_bill.save()
            for detail in self.detail_set.all():
                detail.id = None
                detail.bill = new_bill
                detail.save(check_autoreduce=False)
            Signal.call_signal("change_bill", 'convert', self, new_bill)
            return new_bill
        else:
            return None

    def get_statistics_customer(self, without_reduct):
        cust_list = []
        if self.fiscal_year is not None:
            total_cust = 0
            costumers = {}
            statistics_filter = Q(fiscal_year=self.fiscal_year)
            statistics_filter &= Q(bill_type__in=(Bill.BILLTYPE_BILL, Bill.BILLTYPE_ASSET, Bill.BILLTYPE_RECEIPT))
            statistics_filter &= Q(status__in=(Bill.STATUS_VALID, Bill.STATUS_ARCHIVE))
            for bill in Bill.objects.filter(statistics_filter):
                if bill.third_id not in costumers.keys():
                    costumers[bill.third_id] = 0
                total_excltax = bill.get_total_excltax()
                if without_reduct:
                    total_excltax += bill.get_reduce_excltax()
                if bill.bill_type == Bill.BILLTYPE_ASSET:
                    costumers[bill.third_id] -= total_excltax
                    total_cust -= total_excltax
                else:
                    costumers[bill.third_id] += total_excltax
                    total_cust += total_excltax
            for cust_id in costumers.keys():
                try:
                    ratio = (100 * costumers[cust_id] / total_cust)
                except ZeroDivisionError:
                    ratio = None
                cust_list.append((str(Third.objects.get(id=cust_id)), costumers[cust_id], ratio))
            cust_list.sort(key=lambda cust_item: (-1 * cust_item[1], cust_item[0]))
            cust_list.append(("{[b]}%s{[/b]}" % _('total'), {'format': "{[b]}{0}{[/b]}", 'value': total_cust}, {'format': "{[b]}{0}{[/b]}", 'value': 100}))
        return cust_list

    def get_statistics_article(self, without_reduct, for_quotation):
        art_list = []
        if self.fiscal_year is not None:
            total_art = 0
            articles = {}
            if for_quotation:
                bill_filter = Q(bill__bill_type__in=(Bill.BILLTYPE_QUOTATION, Bill.BILLTYPE_ORDER)) & Q(bill__status=Bill.STATUS_VALID)
            else:
                bill_filter = Q(bill__bill_type__in=(Bill.BILLTYPE_BILL, Bill.BILLTYPE_ASSET, Bill.BILLTYPE_RECEIPT)) & Q(bill__status__in=(Bill.STATUS_VALID, Bill.STATUS_ARCHIVE))
            for det in Detail.objects.filter(Q(bill__fiscal_year=self.fiscal_year) & bill_filter):
                if det.article_id not in articles.keys():
                    articles[det.article_id] = [0, 0]
                total_excltax = det.get_total_excltax()
                if without_reduct:
                    total_excltax += det.get_reduce_excltax()
                if det.bill.bill_type == 2:
                    articles[det.article_id][0] -= total_excltax
                    articles[det.article_id][1] -= float(det.quantity)
                    total_art -= total_excltax
                else:
                    articles[det.article_id][0] += total_excltax
                    articles[det.article_id][1] += float(det.quantity)
                    total_art += total_excltax
            for art_id in articles.keys():
                if art_id is None:
                    art_text = "---"
                else:
                    art_text = str(Article.objects.get(id=art_id))
                if abs(articles[art_id][1]) > 0.0001:
                    try:
                        ratio = (100 * articles[art_id][0] / total_art)
                    except ZeroDivisionError:
                        ratio = 0
                    art_list.append((art_text, articles[art_id][0], articles[art_id][1], articles[art_id][0] / articles[art_id][1], ratio))
            art_list.sort(key=lambda art_item: art_item[1], reverse=True)
            art_list.append(("{[b]}%s{[/b]}" % _('total'), {'format': "{[b]}{0}{[/b]}", 'value': total_art},
                             {'format': "{[b]}{0}{[/b]}", 'value': None}, {'format': "{[b]}{0}{[/b]}", 'value': None},
                             {'format': "{[b]}{0}{[/b]}", 'value': 100.0}))
        return art_list

    def get_statistics_month(self, without_reduct):
        month_list = []
        if self.fiscal_year is not None:
            nb_month = (self.fiscal_year.end.year - self.fiscal_year.begin.year) * 12 + self.fiscal_year.end.month - self.fiscal_year.begin.month + 1
            months = []
            total_month = 0.0
            for current_month in range(nb_month):
                begin_date = same_day_months_after(self.fiscal_year.begin, months=current_month)
                begin_date = begin_date - timedelta(days=begin_date.day - 1)
                end_date = same_day_months_after(begin_date, months=1) - timedelta(days=1)
                amount_sum = 0.0
                for bill in Bill.objects.filter(Q(date__gte=begin_date) & Q(date__lte=end_date) & Q(bill_type__in=(Bill.BILLTYPE_BILL, Bill.BILLTYPE_ASSET, Bill.BILLTYPE_RECEIPT)) & Q(status__in=(Bill.STATUS_VALID, Bill.STATUS_ARCHIVE))):
                    total_excltax = bill.get_total_excltax()
                    if without_reduct:
                        total_excltax += bill.get_reduce_excltax()
                    if bill.bill_type == 2:
                        amount_sum -= total_excltax
                        total_month -= total_excltax
                    else:
                        amount_sum += total_excltax
                        total_month += total_excltax
                months.append((begin_date, amount_sum))
            for begin_date, amount_sum in months:
                try:
                    ratio = (100 * amount_sum / total_month)
                except ZeroDivisionError:
                    ratio = None
                month_list.append((DateFormat(begin_date).format('F Y'), amount_sum, ratio))
            month_list.append(("{[b]}%s{[/b]}" % _('total'), {'format': "{[b]}{0}{[/b]}", 'value': total_month},
                               {'format': "{[b]}{0}{[/b]}", 'value': 100.0}))
        return month_list

    def get_statistics_payoff(self, is_revenu):
        payoff_list = []
        if self.fiscal_year is not None:
            payoffs = []
            nb_payoff = 0
            total_amount = 0
            for mode_id, mode_title in Payoff.get_field_by_name('mode').choices:
                payoff_items = Payoff.objects.filter(supporting__is_revenu=is_revenu, mode=mode_id, supporting__bill__fiscal_year=self.fiscal_year)
                bank_list = payoff_items.values('bank_account').annotate(dcount=Count('bank_account'))
                for bank_item in bank_list:
                    bank = BankAccount.objects.get(id=bank_item['bank_account']) if bank_item['bank_account'] is not None else None
                    payoff_subitems = payoff_items.filter(bank_account=bank)
                    amount = float(payoff_subitems.aggregate(Sum('amount'))['amount__sum'])
                    payoffs.append((mode_title, bank, len(payoff_subitems), amount))
                    total_amount += amount
                    nb_payoff += len(payoff_subitems)
            for payoff_item in payoffs:
                try:
                    ratio = (100 * payoff_item[3] / total_amount)
                except ZeroDivisionError:
                    ratio = None
                payoff_list.append((payoff_item[0], payoff_item[1], payoff_item[2], payoff_item[3], ratio))
            payoff_list.sort(key=lambda payoff_item: payoff_item[3], reverse=True)
            payoff_list.append(("{[b]}%s{[/b]}" % _('total'), None, {'format': "{[b]}{0}{[/b]}", 'value': nb_payoff},
                                {'format': "{[b]}{0}{[/b]}", 'value': total_amount}, {'format': "{[b]}{0}{[/b]}", 'value': 100.0}))
        return payoff_list

    def support_validated(self, validate_date, with_valid=True):
        if (self.bill_type == Bill.BILLTYPE_ASSET) or (self.status != Bill.STATUS_VALID):
            raise LucteriosException(
                IMPORTANT, _("This item can't be validated!"))
        if (self.bill_type == Bill.BILLTYPE_QUOTATION):
            if (Params.getvalue('invoice-order-mode') == Bill.INVOICE_ORDER_CONVERT) and (self.categoryBill is not None) and (self.categoryBill.workflow_order != CategoryBill.WORKFLOWS_NEVER_ORDER):
                new_bill = self.convert_to_order()()
            else:
                new_bill = self.convert_to_bill()
            new_bill.date = validate_date
            new_bill.save()
            if (new_bill is None) or (new_bill.get_info_state() != []):
                raise LucteriosException(IMPORTANT, _("This item can't be validated!"))
            if with_valid:
                new_bill.valid()
        else:
            new_bill = self
        return new_bill

    def get_tax(self):
        try:
            return currency_round(self.get_tax_sum() * self.get_total_rest_topay() / self.get_total_incltax())
        except ZeroDivisionError:
            return None

    def get_payable_without_tax(self):
        if (self.bill_type == Bill.BILLTYPE_ASSET) or (self.status != Bill.STATUS_VALID):
            return 0
        else:
            return self.get_total_rest_topay() - self.get_tax()

    def payoff_have_payment(self):
        return (self.bill_type not in (Bill.BILLTYPE_CART, Bill.BILLTYPE_ASSET)) and (self.status == Bill.STATUS_VALID) and (self.get_total_rest_topay() > 0.001)

    def get_document_filename(self):
        return remove_accent("%s_%s_%s" % (self.billtype, self.num_txt, str(self.third)))

    def get_linked_supportings(self):
        other_bill_inverses = Bill.objects.filter(third=self.third, is_revenu=not self.is_revenu, status__in=(Bill.STATUS_VALID, Bill.STATUS_ARCHIVE)).exclude(bill_type=Bill.BILLTYPE_QUOTATION)
        return [item for item in other_bill_inverses if item.get_total_rest_topay() > 0.001]

    def accounting_of_linked_supportings(self, source_payoff, target_payoff):
        source_bill = source_payoff.supporting.get_final_child()
        target_bill = target_payoff.supporting.get_final_child()
        if isinstance(source_bill, Bill) and isinstance(target_bill, Bill) and (source_payoff.entry is None):
            source_payoff.entry = target_bill.entry
            target_payoff.entry = source_bill.entry
            source_payoff.save(do_internal=False)
            target_payoff.save(do_internal=False)

    def delete_linked_supporting(self, payoff):
        if (payoff.entry is not None) and (payoff.entry.year is not None) and payoff.entry.year.status == FiscalYear.STATUS_FINISHED:
            raise LucteriosException(IMPORTANT, _('Payoff not deletable !'))
        return

    def user_quotation_creator(self):
        invoice = self
        while (invoice is not None) and (invoice.bill_type != Bill.BILLTYPE_QUOTATION):
            invoice = invoice.parentbill
        if invoice is not None:
            create_log = LucteriosLogEntry.objects.filter(Q(modelname=self.get_long_name()) & Q(object_pk=invoice.id) & Q(action=LucteriosLogEntry.Action.CREATE)).last()
            if create_log is not None:
                return LucteriosUser.objects.filter(username=create_log.username).first()
        return None

    def get_email_subject(self):
        if self.categoryBill_id is None:
            return Supporting.get_email_subject(self)
        else:
            if self.categoryBill.with_multi_emailinfo:
                return self.categoryBill.get_multi_emailsubject(self.bill_type)
            else:
                return self.categoryBill.emailsubject

    def get_email_message(self):
        if self.categoryBill_id is None:
            return Supporting.get_email_message(self)
        else:
            if self.categoryBill.with_multi_emailinfo:
                return self.categoryBill.get_multi_emailmessage(self.bill_type)
            else:
                return self.categoryBill.emailmessage

    def get_saved_renew(self):
        return (self.fiscal_year is not None) and (self.fiscal_year.status != FiscalYear.STATUS_FINISHED)

    def get_default_print_model(self):
        model = None
        if self.categoryBill_id is not None:
            if self.bill_type in (Bill.BILLTYPE_QUOTATION, Bill.BILLTYPE_CART):
                model = self.categoryBill.printmodel_id
            else:
                model = self.categoryBill.printmodel_sold_id
        if model is None:
            return Supporting.get_default_print_model(self)
        else:
            return model

    def get_payment_method(self):
        from diacamma.invoice.views_summary import InvoiceValidQuotation
        if self.categoryBill_id is None:
            payment_methods = list(Supporting.get_payment_method(self))
        else:
            payment_methods = list(self.categoryBill.payment_method.all())
        if (self.bill_type == Bill.BILLTYPE_QUOTATION) and (Params.getvalue('invoice-order-mode') == Bill.INVOICE_ORDER_LINK) and ((self.categoryBill is None) or (self.categoryBill.workflow_order != CategoryBill.WORKFLOWS_NEVER_ORDER)):
            payment_methods.insert(0, InvoiceValidQuotation.PaymentMethodValidate(self))
        return payment_methods

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.bill_type = int(self.bill_type)
        if self.id is not None:
            for detail in self.detail_set.all():
                if detail.define_autoreduce():
                    detail.save()
        return Supporting.save(self, force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    class Meta(object):
        verbose_name = _('bill')
        verbose_name_plural = _('bills')
        ordering = ['-date', 'status']
        default_permissions = ['add', 'change', 'delete', 'archive', 'asset', 'cart']


class Detail(LucteriosModel):
    bill = models.ForeignKey(Bill, verbose_name=_('bill'), null=False, db_index=True, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, verbose_name=_('article'), null=True, default=None, db_index=True, on_delete=models.PROTECT)
    designation = models.TextField(verbose_name=_('designation'))
    price = LucteriosDecimalField(verbose_name=_('price'), max_digits=10, decimal_places=3,
                                  default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(9999999.999)], format_string=lambda: format_with_devise(5))
    unit = models.CharField(verbose_name=_('unit'), null=True, default='', max_length=10)
    quantity = LucteriosDecimalField(verbose_name=_('quantity'), max_digits=12, decimal_places=3,
                                     default=1.0, validators=[MinValueValidator(0.0), MaxValueValidator(9999999.999)], format_string="N3")
    reduce = LucteriosDecimalField(verbose_name=_('reduce'), max_digits=10, decimal_places=3,
                                   default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(9999999.999)], format_string=lambda: format_with_devise(5))
    vta_rate = LucteriosDecimalField(_('vta rate'), max_digits=6, decimal_places=4,
                                     default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)], format_string=lambda: format_with_devise(5))
    storagearea = models.ForeignKey(StorageArea, verbose_name=_('storage area'), null=True, default=None, db_index=True, on_delete=models.PROTECT)

    quantity_txt = LucteriosVirtualField(verbose_name=_('quantity'), compute_from="get_quantity_txt")
    price_txt = LucteriosVirtualField(verbose_name=_('price'), compute_from="get_price", format_string=lambda: format_with_devise(5))
    reduce_txt = LucteriosVirtualField(verbose_name=_('reduce'), compute_from="get_reduce_txt")
    total = LucteriosVirtualField(verbose_name=_('total'), compute_from='get_total_ex', format_string=lambda: format_with_devise(5))

    reduce_amount = LucteriosVirtualField(verbose_name=_('reduce'), compute_from="get_reduce", format_string=lambda: format_with_devise(5))
    reduce_amount_txt = LucteriosVirtualField(verbose_name=_('reduce'), compute_from="get_reduce", format_string=lambda: format_with_devise(5))

    total_excltax = LucteriosVirtualField(verbose_name=_('total'), compute_from="get_total_excltax", format_string=lambda: format_with_devise(5))
    total_incltax = LucteriosVirtualField(verbose_name=_('total incl. taxes'), compute_from="get_total_incltax", format_string=lambda: format_with_devise(5))
    price_vta = LucteriosVirtualField(verbose_name=_('VTA sum'), compute_from="get_vta", format_string=lambda: format_with_devise(5))

    article_fake = LucteriosVirtualField(verbose_name=_('article'), compute_from=lambda _this: "article fake")

    def __init__(self, *args, **kwargs):
        LucteriosModel.__init__(self, *args, **kwargs)
        self.filter_thirdid = 0
        self.filter_ref = ''

    def set_context(self, xfer):
        qty_field = self.get_field_by_name('quantity')
        if self.article_id is not None:
            qty_field.decimal_places = self.article.qtyDecimal
        else:
            qty_field.decimal_places = 3
        self.filter_thirdid = xfer.getparam('third', 0)
        self.filter_ref = xfer.getparam('reference', '')
        self.filter_cat = xfer.getparam('cat_filter', ())
        self.filter_lib = xfer.getparam('ref_filter', '')

    @property
    def article_query(self):
        artfilter = Q(isdisabled=False)
        artfilter &= ~Q(stockable=Article.STOCKABLE_YES_WITHOUTSELL)
        if self.filter_thirdid != 0:
            artfilter &= Q(provider__third_id=self.filter_thirdid)
        if self.filter_ref != '':
            artfilter &= Q(provider__reference__icontains=self.filter_ref)
        if self.filter_lib != '':
            artfilter &= Q(reference__icontains=self.filter_lib) | Q(designation__icontains=self.filter_lib)
        items = Article.objects.filter(artfilter).distinct()
        if len(self.filter_cat) > 0:
            for cat_item in Category.objects.filter(id__in=self.filter_cat).distinct():
                items = items.filter(categories__in=[cat_item]).distinct()
        return items

    def __str__(self):
        return "[%s] %s:%s" % (str(self.article), str(self.designation), self.price_txt)

    def get_auditlog_object(self):
        return self.bill.get_final_child()

    @classmethod
    def get_default_fields(cls):
        return ["article", "designation", "price", "unit", "quantity_txt", "storagearea", "reduce_txt", 'total']

    @classmethod
    def get_edit_fields(cls):
        return ["article_fake", "designation", ("price", "reduce"), ("quantity", "unit"), "storagearea"]

    @classmethod
    def get_show_fields(cls):
        return ["article", "designation", "price", "unit", "quantity_txt", "reduce_txt", "storagearea"]

    @classmethod
    def get_print_fields(cls):
        res = cls.get_default_fields()
        last = res[-1]
        del res[-1]
        res.append((_('reduce amount'), "reduce_amount_txt"))
        res.append((_('reduce ratio'), "reduce_ratio_txt"))
        res.append(last)
        return res

    @classmethod
    def get_search_fields(cls):
        fieldnames = ["designation", "price", "unit", "quantity"]
        for fieldname in Article.get_search_fields():
            fieldnames.append(cls.convert_field_for_search("article", fieldname))
        return fieldnames

    @classmethod
    def create_for_bill(cls, bill, article, qty=1, reduce=0.0, designation=None):
        newdetail = cls(bill=bill, article=article, designation=article.designation if (designation is None) else designation,
                        price=article.price, unit=article.unit, quantity=qty, reduce=reduce)
        newdetail.editor.before_save(None)
        newdetail.save()
        return newdetail

    def get_quantity_txt(self):
        if self.article is not None:
            return format_value(self.quantity, "N%d" % self.article.qtyDecimal)
        else:
            return format_value(self.quantity, "N3")

    def get_price(self):
        if (Params.getvalue("invoice-vat-mode") == Vat.MODE_PRICEWITHVAT) and (self.vta_rate > 0.001):
            return currency_round(self.price * self.vta_rate)
        if (Params.getvalue("invoice-vat-mode") == Vat.MODE_PRICENOVAT) and (self.vta_rate < -0.001):
            return currency_round(self.price * -1 * self.vta_rate / (1 - self.vta_rate))
        return float(self.price)

    def get_reduce(self):
        if (Params.getvalue("invoice-vat-mode") == Vat.MODE_PRICEWITHVAT) and (self.vta_rate > 0.001):
            return currency_round(self.reduce * self.vta_rate)
        if (Params.getvalue("invoice-vat-mode") == Vat.MODE_PRICENOVAT) and (self.vta_rate < -0.001):
            return currency_round(self.reduce * -1 * self.vta_rate / (1 - self.vta_rate))
        return float(self.reduce)

    @property
    def reduce_ratio_txt(self):
        if self.reduce > 0.0001:
            try:
                red_ratio = "%.2f%%" % (100 * self.get_reduce() / (self.get_price() * float(self.quantity)),)
            except ZeroDivisionError:
                red_ratio = ''
            return red_ratio
        else:
            return None

    def get_reduce_txt(self):
        if self.id is None:
            return None
        if self.reduce > 0.0001:
            if Params.getvalue('invoice-reduce-with-ratio'):
                red_ratio = self.reduce_ratio_txt
                if red_ratio != '':
                    red_ratio = "(%s)" % red_ratio
            else:
                red_ratio = ''
            return "%s%s" % (get_amount_from_format_devise(self.reduce_amount, 7), red_ratio)
        else:
            return None

    def get_total_ex(self):
        if Params.getvalue("invoice-vat-mode") == Vat.MODE_PRICEWITHVAT:
            return self.get_total_incltax()
        elif Params.getvalue("invoice-vat-mode") == Vat.MODE_PRICENOVAT:
            return self.get_total_excltax()
        else:
            return self.get_total()

    def get_total(self):
        if self.id is None:
            return 0
        return currency_round(float(self.price) * float(self.quantity) - float(self.reduce))

    def get_total_excltax(self):
        if self.id is None:
            return 0
        if self.vta_rate < -0.001:
            return self.get_total() - self.get_vta()
        else:
            return self.get_total()

    def get_reduce_vat(self):
        if self.id is None:
            return 0
        if self.vta_rate < -0.001:
            return currency_round(self.reduce * -1 * self.vta_rate / (1 - self.vta_rate))
        elif self.vta_rate > 0.001:
            return currency_round(self.reduce * self.vta_rate)
        else:
            return 0

    def get_reduce_excltax(self):
        if self.id is None:
            return 0
        if self.vta_rate < -0.001:
            return currency_round(self.reduce) - self.get_reduce_vat()
        else:
            return currency_round(self.reduce)

    def get_total_incltax(self):
        if self.id is None:
            return 0
        if self.vta_rate > 0.001:
            return self.get_total() + self.get_vta()
        else:
            return self.get_total()

    def get_vta(self):
        if self.id is None:
            return 0
        val = 0
        if self.vta_rate > 0.001:
            val = currency_round(self.price * self.quantity * self.vta_rate)
        elif self.vta_rate < -0.001:
            val = currency_round(
                self.price * self.quantity * -1 * self.vta_rate / (1 - self.vta_rate))
        val -= self.get_reduce_vat()
        return val

    def define_autoreduce(self):
        if (self.bill.third_id is not None) and (self.bill.status in (Bill.STATUS_BUILDING, Bill.STATUS_VALID)) and (float(self.reduce) < 0.0001):
            for red_item in AutomaticReduce.objects.all():
                if self.bill.bill_type != Bill.BILLTYPE_ASSET:
                    self.reduce = max(float(self.reduce), red_item.calcul_reduce(self))
                else:
                    new_reduce = red_item.calcul_reduce(self)
                    if abs(new_reduce) > 0.001:
                        if float(self.reduce) < 0.0001:
                            self.reduce = new_reduce
                        else:
                            self.reduce = min(float(self.reduce), new_reduce)
            return float(self.reduce) > 0.0001
        return False

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, check_autoreduce=True):
        if check_autoreduce:
            self.define_autoreduce()
        return LucteriosModel.save(self, force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    class Meta(object):
        verbose_name = _('detail')
        verbose_name_plural = _('details')
        default_permissions = []


class StorageSheet(LucteriosModel):
    STATUS_BUILDING = 0
    STATUS_VALID = 1
    LIST_STATUS = ((STATUS_BUILDING, _('building storage')), (STATUS_VALID, _('valid storage')))

    TYPE_RECEIPT = 0
    TYPE_EXIT = 1
    TYPE_TRANSFER = 2
    LIST_TYPES = ((TYPE_RECEIPT, _('stock receipt')), (TYPE_EXIT, _('stock exit')), (TYPE_TRANSFER, _('stock transfer')))

    sheet_type = models.IntegerField(verbose_name=_('sheet type'), choices=LIST_TYPES, null=False, default=TYPE_RECEIPT, db_index=True)
    date = models.DateField(verbose_name=_('date'), null=False)
    storagearea = models.ForeignKey(StorageArea, verbose_name=_('storage area'), null=False, db_index=True, on_delete=models.PROTECT)
    comment = models.TextField(_('comment'))
    status = FSMIntegerField(verbose_name=_('status'), choices=LIST_STATUS, null=False, default=STATUS_BUILDING, db_index=True)

    provider = models.ForeignKey(Third, verbose_name=_('provider'), null=True, default=None, on_delete=models.PROTECT)
    bill_reference = models.CharField(_('bill reference'), blank=True, max_length=50)
    bill_date = models.DateField(verbose_name=_('bill date'), null=True)

    total = LucteriosVirtualField(verbose_name=_('total amount'), compute_from="get_total", format_string=lambda: format_with_devise(5))

    def __str__(self):
        sheettype = get_value_if_choices(self.sheet_type, self.get_field_by_name('sheet_type'))
        sheetstatus = get_value_if_choices(self.status, self.get_field_by_name('status'))
        return "%s - %s [%s]" % (sheettype, get_date_formating(self.date), sheetstatus)

    @classmethod
    def get_default_fields(cls):
        return ["sheet_type", "status", "date", "storagearea", "comment"]

    @classmethod
    def get_edit_fields(cls):
        return [("sheet_type",), ("date", "storagearea"), ("provider", "bill_date"), ("bill_reference"), ("comment",)]

    @classmethod
    def get_show_fields(cls):
        return [("sheet_type", "status"), ("date", "storagearea"), ("provider", "bill_date"), ("bill_reference"), ("comment",), ("storagedetail_set",), ('total',)]

    @classmethod
    def get_search_fields(cls):
        search_fields = ["sheet_type", "status", "date", "storagearea", "comment"]
        for fieldname in StorageDetail.get_search_fields():
            search_fields.append(cls.convert_field_for_search("storagedetail_set", fieldname))
        return search_fields

    @property
    def provider_query(self):
        thirdfilter = Q(accountthird__code__regex=current_system_account().get_provider_mask())
        return Third.objects.filter(thirdfilter).distinct()

    def can_delete(self):
        if self.status != self.STATUS_BUILDING:
            return _('"%s" cannot be deleted!') % str(self)
        return ''

    def get_total(self):
        value = 0.0
        if self.id is not None:
            for detail in self.storagedetail_set.all():
                value += float(detail.quantity) * float(detail.price)
        return value

    def get_info_state(self):
        info = []
        if self.id is not None:
            for detail in self.storagedetail_set.all():
                if detail.article.stockable == Article.STOCKABLE_NO:
                    info.append(_("Article %s is not stockable") % str(detail.article))
                elif (self.sheet_type != self.TYPE_RECEIPT) and not detail.article.has_sufficiently(self.storagearea_id, detail.quantity):
                    info.append(_("Article %s is not sufficiently stocked") % str(detail.article))
        return info

    transitionname__valid = _("Validate")

    @transition(field=status, source=STATUS_BUILDING, target=STATUS_VALID, conditions=[lambda item:item.get_info_state() == []])
    def valid(self):
        if self.sheet_type == self.TYPE_EXIT:
            for detail in self.storagedetail_set.all():
                detail.quantity = -1 * abs(detail.quantity)
                detail.save()

    def create_oposit(self, target_area):
        other = StorageSheet()
        other.status = self.STATUS_BUILDING
        other.date = self.date
        other.comment = self.comment
        other.sheet_type = self.TYPE_RECEIPT
        other.storagearea_id = target_area
        other.save()
        for detail in self.storagedetail_set.all():
            detail.id = None
            detail.storagesheet_id = other.id
            detail.save()
        return other

    class Meta(object):
        verbose_name = _('storage sheet')
        verbose_name_plural = _('storage sheets')
        ordering = ['-date', 'status']


class StorageDetail(LucteriosModel):
    storagesheet = models.ForeignKey(StorageSheet, verbose_name=_('storage sheet'), null=False, db_index=True, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, verbose_name=_('article'), null=False, db_index=True, on_delete=models.PROTECT)
    price = LucteriosDecimalField(verbose_name=_('buying price'), max_digits=10, decimal_places=3, default=0.0,
                                  validators=[MinValueValidator(0.0), MaxValueValidator(9999999.999)], format_string=lambda: format_with_devise(5) + ";---;---")
    quantity = models.DecimalField(verbose_name=_('quantity'), max_digits=12, decimal_places=3, default=1.0,
                                   validators=[MinValueValidator(0.0), MaxValueValidator(9999999.999)])
    quantity_txt = LucteriosVirtualField(verbose_name=_('quantity'), compute_from="get_quantity_txt")

    article_fake = LucteriosVirtualField(verbose_name=_('article'), compute_from=lambda _this: "article fake")

    def __str__(self):
        return "%s %d" % (self.article_id, self.quantity)

    def get_auditlog_object(self):
        return self.storagesheet.get_final_child()

    @classmethod
    def get_default_fields(cls):
        return ["article", "price", "quantity_txt"]

    @classmethod
    def get_edit_fields(cls):
        return ["article_fake", "price", "quantity"]

    @classmethod
    def get_show_fields(cls):
        return ["article", "price", "quantity_txt"]

    @classmethod
    def get_search_fields(cls):
        search_fields = ["price", "quantity"]
        for fieldname in Article.get_search_fields():
            search_fields.append(cls.convert_field_for_search("article", fieldname))
        return search_fields

    @classmethod
    def get_import_fields(cls):
        return ["article", "price", "quantity"]

    def get_quantity_txt(self):
        if self.quantity is None:
            return None
        if self.article_id is not None:
            format_txt = "N%d" % self.article.qtyDecimal
        else:
            format_txt = "N3"
        return format_to_string(float(self.quantity), format_txt, None)

    def set_context(self, xfer):
        qty_field = self.get_field_by_name('quantity')
        if self.article_id is not None:
            qty_field.decimal_places = self.article.qtyDecimal
        else:
            qty_field.decimal_places = 3
        self.filter_thirdid = xfer.getparam('third', 0)
        self.filter_ref = xfer.getparam('reference', '')
        self.filter_cat = xfer.getparam('cat_filter', ())
        self.filter_lib = xfer.getparam('ref_filter', '')

    @property
    def article_query(self):
        artfilter = Q(isdisabled=False)
        artfilter &= Q(stockable__in=(Article.STOCKABLE_YES, Article.STOCKABLE_YES_WITHOUTSELL))
        if self.filter_thirdid != 0:
            artfilter &= Q(provider__third_id=self.filter_thirdid)
        if self.filter_ref != '':
            artfilter &= Q(provider__reference__icontains=self.filter_ref)
        if self.filter_lib != '':
            artfilter &= Q(reference__icontains=self.filter_lib) | Q(designation__icontains=self.filter_lib)
        items = Article.objects.filter(artfilter).distinct()
        if len(self.filter_cat) > 0:
            for cat_item in Category.objects.filter(id__in=self.filter_cat).distinct():
                items = items.filter(categories__in=[cat_item]).distinct()
        return items

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if (self.storagesheet.status == StorageSheet.STATUS_BUILDING) and (int(self.storagesheet.sheet_type) == StorageSheet.TYPE_TRANSFER):
            art = self.article
            art.show_storagearea = self.storagesheet.storagearea_id
            stock_val = art.get_stockage_values()
            if (len(stock_val) > 1) and (stock_val[0][0] == self.storagesheet.storagearea_id):
                self.price = stock_val[0][3] / stock_val[0][2]
            else:
                self.price = 0.0
        return LucteriosModel.save(self, force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    class Meta(object):
        verbose_name = _('storage detail')
        verbose_name_plural = _('storage details')
        default_permissions = []


class ArticleSituationSet(QuerySet):

    def __init__(self, model=None, query=None, using=None, hints=None):
        QuerySet.__init__(self, model=ArticleSituation, query=query, using=using, hints=hints)
        self._result_cache = None
        self.pt_id = 0
        self.model._meta.pk = Article()._meta.pk
        self.categories_filter = self._hints['categories_filter']
        self.hide_empty = self._hints['hide_empty']
        self.filter = self._hints['filter']
        self.total_amount = 0

    def _fetch_all(self):
        if self._result_cache is None:
            self._result_cache = []
            self.pt_id = 1
            self.total_amount = 0
            items = StorageDetail.objects.filter(self.filter)
            if len(self.categories_filter) > 0:
                for cat_item in Category.objects.filter(id__in=self.categories_filter):
                    items = items.filter(article__categories__in=[cat_item])
            item_id = 0
            for item in items.values('article', 'storagesheet__storagearea').annotate(data_sum=Sum('quantity')):
                if (item['data_sum'] > 0) or not self.hide_empty:
                    item_id += 1
                    area_id = item['storagesheet__storagearea']
                    art = Article.objects.get(id=item['article'])
                    qty = float(item['data_sum'])
                    amount = float(art.get_amount_from_area(qty, area_id))
                    self.total_amount += amount
                    self._result_cache.append(ArticleSituation(id=item_id,
                                                               article=art,
                                                               storagearea_id=area_id,
                                                               amount=amount,
                                                               quantity=qty))


class ArticleSituation(LucteriosModel):
    article = models.ForeignKey(Article, verbose_name=_('article'), null=False, db_index=True, on_delete=models.DO_NOTHING)
    storagearea = models.ForeignKey(StorageArea, verbose_name=_('storage area'), null=False, db_index=True, on_delete=models.DO_NOTHING)
    amount = LucteriosDecimalField(verbose_name=_('buying price'), max_digits=10, decimal_places=3, default=0.0,
                                   validators=[MinValueValidator(0.0), MaxValueValidator(9999999.999)], format_string=lambda: format_with_devise(5))
    quantity = models.DecimalField(verbose_name=_('quantity'), max_digits=12, decimal_places=3, default=1.0,
                                   validators=[MinValueValidator(0.0), MaxValueValidator(9999999.999)])
    quantity_txt = LucteriosVirtualField(verbose_name=_('quantity'), compute_from="get_quantity_txt")
    mean = LucteriosVirtualField(verbose_name=_('mean'), compute_from="get_mean", format_string=lambda: format_with_devise(5))
    designation = LucteriosVirtualField(verbose_name=_('designation'), compute_from=lambda item: item.article.designation)

    @classmethod
    def get_default_fields(cls):
        fields = ['article', 'designation']
        fields.extend(['storagearea', 'quantity_txt', 'amount', 'mean'])
        return fields

    def get_quantity_txt(self):
        if self.quantity is None:
            return None
        if self.article_id is not None:
            format_txt = "N%d" % self.article.qtyDecimal
        else:
            format_txt = "N3"
        return format_to_string(float(self.quantity), format_txt, None)

    def get_mean(self):
        if (self.quantity is not None) and (self.quantity > 0.0001):
            return self.amount / self.quantity
        else:
            return None

    class Meta(object):
        default_permissions = []
        verbose_name = _('article situation')
        verbose_name_plural = _('articles situations')


class AutomaticReduce(LucteriosModel):
    MODE_BYVALUE = 0
    MODE_BYPERCENT = 1
    MODE_BYPERCENTSOLD = 2
    LIST_MODES = ((MODE_BYVALUE, _('by value')), (MODE_BYPERCENT, _('by percentage')), (MODE_BYPERCENTSOLD, _('by overall percentage sold')))

    name = models.CharField(_('name'), max_length=250, blank=False)
    category = models.ForeignKey(Category, verbose_name=_('category'), null=False, on_delete=models.PROTECT)
    mode = models.IntegerField(verbose_name=_('mode'), choices=LIST_MODES, null=False, default=MODE_BYVALUE)
    amount = models.DecimalField(verbose_name=_('amount'), max_digits=10, decimal_places=3, default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(9999999.999)])
    occurency = models.IntegerField(verbose_name=_('occurency'), default=0, validators=[MinValueValidator(0), MaxValueValidator(1000)])
    filtercriteria = models.ForeignKey(SavedCriteria, verbose_name=_('filter criteria'), null=True, on_delete=models.PROTECT)

    amount_txt = LucteriosVirtualField(verbose_name=_('amount'), compute_from="get_amount_txt")

    def __str__(self):
        return self.name

    @classmethod
    def get_default_fields(cls):
        return ["name", "category", "mode", "amount_txt", "occurency", "filtercriteria"]

    @classmethod
    def get_edit_fields(cls):
        return ["name", "category", "mode", "amount", "occurency", "filtercriteria"]

    @classmethod
    def get_show_fields(cls):
        return ["name", "category", "mode", "amount_txt", "occurency", "filtercriteria"]

    @property
    def filtercriteria_query(self):
        return SavedCriteria.objects.filter(modelname=Third.get_long_name())

    def _get_nb_sold(self, reduce_query):
        nb_sold = 0.0
        if self.occurency != 0:
            detail_reduce = Detail.objects.filter(reduce_query).annotate(direction=Case(When(bill__bill_type=Bill.BILLTYPE_ASSET, then=-1),
                                                                                        default=1, output_field=IntegerField()))
            qty_val = detail_reduce.aggregate(data_sum=Sum(F('quantity') * F('direction'), output_field=FloatField()))
            if qty_val['data_sum'] is not None:
                nb_sold = float(qty_val['data_sum'])
        else:
            nb_sold = 0.0
            self.occurency = 1
        return nb_sold

    def _reduce_for_mode2(self, reduce_query, detail, nb_sold):
        amount_sold = 0.0
        detail_reduce = Detail.objects.filter(reduce_query).annotate(direction=Case(When(bill__bill_type=Bill.BILLTYPE_ASSET, then=-1),
                                                                                    default=1, output_field=IntegerField()))
        amount_val = detail_reduce.aggregate(data_sum=Sum(F('quantity') * F('price') * F('direction'), output_field=FloatField()))
        if amount_val['data_sum'] is not None:
            amount_sold = float(amount_val['data_sum'])
        reduce_sold = 0.0
        reduce_val = detail_reduce.aggregate(data_sum=Sum(F('reduce') * F('direction'), output_field=FloatField()))
        if reduce_val['data_sum'] is not None:
            reduce_sold = float(reduce_val['data_sum'])
        if detail.bill.bill_type != Bill.BILLTYPE_ASSET:
            amount_sold += float(detail.quantity) * float(detail.price)
            return amount_sold * float(self.amount) / 100.0 - reduce_sold
        else:
            if (nb_sold - float(detail.quantity)) < self.occurency:
                return reduce_sold
            else:
                amount_sold -= float(detail.quantity) * float(detail.price)
                return reduce_sold - amount_sold * float(self.amount) / 100.0

    def check_filtercriteria(self, third_id):
        if self.filtercriteria_id is not None:
            from lucterios.framework.xfersearch import get_search_query_from_criteria
            filter_result, _desc = get_search_query_from_criteria(self.filtercriteria.criteria, Third)
            third_list = Third.objects.filter(filter_result).distinct()
            return third_list.filter(id=third_id).exists()
        return True

    def calcul_reduce(self, detail):
        val_reduce = 0.0
        if (detail.bill.third_id is not None) and (detail.bill.status in (Bill.STATUS_BUILDING, Bill.STATUS_VALID)) and (detail.article_id is not None) and \
                self.category.article_set.filter(id=detail.article_id).exists() and self.check_filtercriteria(detail.bill.third_id):
            current_year = FiscalYear.get_current()
            reduce_query = Q(bill__third=detail.bill.third) & Q(article__categories=self.category)
            reduce_query &= (Q(bill__bill_type__in=(Bill.BILLTYPE_RECEIPT, Bill.BILLTYPE_BILL, Bill.BILLTYPE_ASSET)) & Q(bill__status__in=(Bill.STATUS_BUILDING, Bill.STATUS_VALID, Bill.STATUS_ARCHIVE))) | (Q(bill__bill_type=Bill.BILLTYPE_QUOTATION) & Q(bill__status__in=(Bill.STATUS_BUILDING, Bill.STATUS_VALID)))
            reduce_query &= Q(bill__date__gte=current_year.begin) & Q(bill__date__lte=current_year.end)
            if detail.id is not None:
                reduce_query &= ~Q(id=detail.id)
            nb_sold = self._get_nb_sold(reduce_query)
            if detail.bill.bill_type != Bill.BILLTYPE_ASSET:
                nb_sold += float(detail.quantity)
            if self.occurency <= nb_sold:
                qty_reduce = min(float(detail.quantity), nb_sold - self.occurency + 1)
                if self.mode == self.MODE_BYVALUE:
                    val_reduce = qty_reduce * float(self.amount)
                elif self.mode == self.MODE_BYPERCENT:
                    val_reduce = qty_reduce * float(detail.price) * float(self.amount) / 100.0
                else:
                    val_reduce = self._reduce_for_mode2(reduce_query, detail, nb_sold)
        return min(val_reduce, float(detail.quantity) * float(detail.price))

    def get_amount_txt(self):
        if self.amount is None:
            return None
        if self.mode == self.MODE_BYVALUE:
            return format_to_string(float(self.amount), format_with_devise(7), None)
        else:
            return "%.2f%%" % float(self.amount)

    class Meta(object):
        verbose_name = _('automatic reduce')
        verbose_name_plural = _('automatic reduces')
        default_permissions = []


class InventorySheet(LucteriosModel):
    STATUS_BUILDING = 0
    STATUS_VALID = 1
    LIST_STATUS = ((STATUS_BUILDING, _('building')), (STATUS_VALID, _('valid')))

    date = models.DateField(verbose_name=_('date'), null=False)
    storagearea = models.ForeignKey(StorageArea, verbose_name=_('storage area'), null=False, db_index=True, on_delete=models.PROTECT)
    comment = models.TextField(_('comment'))
    status = FSMIntegerField(verbose_name=_('status'), choices=LIST_STATUS, null=False, default=STATUS_BUILDING, db_index=True)
    stockreceipt = models.ForeignKey(StorageSheet, verbose_name=_('stock receipt'), null=True, db_index=True, on_delete=models.SET_NULL, related_name='receipt_storagesheet')
    stockexit = models.ForeignKey(StorageSheet, verbose_name=_('stock exit'), null=True, db_index=True, on_delete=models.SET_NULL, related_name='exit_storagesheet')

    def __str__(self):
        sheetstatus = get_value_if_choices(self.status, self.get_field_by_name('status'))
        return "%s [%s]" % (get_date_formating(self.date), sheetstatus)

    @classmethod
    def get_default_fields(cls):
        return ["date", "storagearea", "status", "comment"]

    @classmethod
    def get_edit_fields(cls):
        return [("date", "storagearea"), ("comment",)]

    @classmethod
    def get_show_fields(cls):
        return [("date", "status"), ("storagearea",), ("comment",)]

    def can_delete(self):
        if self.status > 0:
            return _('"%s" cannot be deleted!') % str(self)
        return ''

    def can_valid(self):
        if self.status == self.STATUS_BUILDING:
            for detail in self.inventorydetail_set.all():
                if detail.quantity is None:
                    return False
            return self.inventorydetail_set.all().count() > 0
        else:
            return False

    transitionname__valid = _("Validate")

    @transition(field=status, source=STATUS_BUILDING, target=STATUS_VALID, conditions=[lambda item:item.can_valid()])
    def valid(self):
        stockreceipt = StorageSheet.objects.create(status=StorageSheet.STATUS_BUILDING, date=self.date, comment=_('Receipt from inventory'),
                                                   sheet_type=StorageSheet.TYPE_RECEIPT, storagearea=self.storagearea)
        stockexit = StorageSheet.objects.create(status=StorageSheet.STATUS_BUILDING, date=self.date, comment=_('Exit from inventory'),
                                                sheet_type=StorageSheet.TYPE_EXIT, storagearea=self.storagearea)
        for detail in self.inventorydetail_set.all():
            diff_quantity = float(detail.quantity) - float(detail.get_real_quantity())
            if (diff_quantity) < -1e-3:
                StorageDetail.objects.create(storagesheet=stockexit, article=detail.article, price=0, quantity=abs(diff_quantity))
            elif (diff_quantity) > 1e-3:
                StorageDetail.objects.create(storagesheet=stockreceipt, article=detail.article, price=0, quantity=abs(diff_quantity))
        if stockreceipt.storagedetail_set.all().count() > 0:
            stockreceipt.valid()
            self.stockreceipt = stockreceipt
        else:
            stockreceipt.delete()
        if stockexit.storagedetail_set.all().count() > 0:
            stockexit.valid()
            self.stockexit = stockexit
        else:
            stockexit.delete()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        res = LucteriosModel.save(self, force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
        if int(self.status) == self.STATUS_BUILDING:
            for article in Article.objects.filter(Q(isdisabled=False) & Q(stockable__in=(1, 2))).order_by('reference').distinct():
                InventoryDetail.objects.get_or_create(article=article, inventorysheet=self)
        return res

    class Meta(object):
        verbose_name = _('inventory sheet')
        verbose_name_plural = _('inventory sheets')
        ordering = ['-date', 'status']


class InventoryDetail(LucteriosModel):
    inventorysheet = models.ForeignKey(InventorySheet, verbose_name=_('inventory sheet'), null=False, db_index=True, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, verbose_name=_('article'), null=False, db_index=True, on_delete=models.PROTECT)
    quantity = models.DecimalField(verbose_name=_('counted quantity'), null=True, max_digits=12, decimal_places=3, default=None,
                                   validators=[MinValueValidator(0.0), MaxValueValidator(9999999.999)])
    quantity_txt = LucteriosVirtualField(verbose_name=_('counted quantity'), compute_from="get_quantity_txt")

    real_quantity = LucteriosVirtualField(verbose_name=_('current quantity'), compute_from="get_real_quantity")
    real_quantity_txt = LucteriosVirtualField(verbose_name=_('current quantity'), compute_from="get_real_quantity_txt")

    def __str__(self):
        return "%s %d" % (self.article, self.quantity)

    def get_auditlog_object(self):
        return self.inventorysheet.get_final_child()

    @classmethod
    def get_default_fields(cls):
        fields = ["article", "article.designation", "article.last_buy_price", "article.mean_buy_price"]
        fields.extend([(field.name, "article." + field.get_fieldname()) for field in CustomField.get_filter(Article) if field.get_fieldname() in Article.get_custom_fields()])
        fields.extend(["real_quantity_txt", "quantity_txt"])
        return fields

    @classmethod
    def get_edit_fields(cls):
        return ["real_quantity", "quantity"]

    def get_quantity_txt(self):
        if self.quantity is None:
            return None
        if self.article_id is not None:
            format_txt = "N%d" % self.article.qtyDecimal
        else:
            format_txt = "N3"
        return format_to_string(float(self.quantity), format_txt, None)

    def get_real_quantity(self):
        if self.article_id is None:
            return 0
        try:
            real_quantity = self.article.get_stockage_total_num(self.inventorysheet.storagearea_id)
            if real_quantity is None:
                return 0
            return real_quantity
        except Exception:
            getLogger('diacamma.invoice').exception("get_real_quantity")
            raise

    def get_real_quantity_txt(self):
        if self.article_id is None:
            return None
        format_txt = "N%d" % self.article.qtyDecimal
        return format_to_string(float(self.get_real_quantity()), format_txt, None)

    def copy_value(self):
        self.quantity = self.get_real_quantity()
        self.save()

    class Meta(object):
        verbose_name = _('inventory detail')
        verbose_name_plural = _('inventory details')
        default_permissions = []


def get_or_create_customer(contact_id):
    if contact_id == 1:
        raise LucteriosException(GRAVE, "Current structure can't be third !")
    try:
        third = Third.objects.get(contact_id=contact_id)
    except ObjectDoesNotExist:
        third = Third.objects.create(
            contact_id=contact_id, status=0)
        AccountThird.objects.create(
            third=third, code=Params.getvalue("invoice-account-third"))
    return third


def convert_articles():
    for art in Article.objects.filter(Q(accountposting__isnull=True) & ~Q(sell_account='')).distinct():
        accout_post, created = AccountPosting.objects.get_or_create(sell_account=art.sell_account)
        if created:
            account = ChartsAccount.get_chart_account(accout_post.sell_account)
            accout_post.name = account.name[:100]
            accout_post.save()
        art.accountposting = accout_post
        art.sell_account = ''
        art.save()


def correct_quotation_asset_account():
    nb_quotation_correct = 0
    nb_asset_correct = 0
    for bill in Bill.objects.filter(Q(bill_type__in=(Bill.BILLTYPE_QUOTATION, Bill.BILLTYPE_ASSET)) and Q(entry__close=False)):
        if bill.bill_type == Bill.BILLTYPE_QUOTATION:
            corrected = False
            if bill.entry_id is not None:
                entry = bill.entry
                bill.entry = None
                bill.save()
                entry.delete()
                corrected = True
            for payoff in bill.payoff_set.filter(Q(entry__isnull=True) | Q(entry__close=False)):
                payoff.delete()
                corrected = True
            if corrected:
                nb_quotation_correct += 1
        elif bill.bill_type == Bill.BILLTYPE_ASSET:
            corrected = False
            if not bill.entry.is_asset:
                bill.entry.reverse_entry()
                corrected = True
            for payoff in bill.payoff_set.filter(Q(entry__close=False)):
                if not payoff.entry.is_asset:
                    payoff.entry.reverse_entry()
                    corrected = True
            if corrected:
                nb_asset_correct += 1
    if (nb_quotation_correct > 0) or (nb_asset_correct > 0):
        getLogger("diacamma.invoice").info(" * account correction assert = %d / quotation = %s", nb_asset_correct, nb_quotation_correct)


@Signal.decorate('costaccounting_change')
def invoice_changecost_model(new_cost, lastcost, old_cost):
    for model in AccountPosting.objects.filter(cost_accounting=old_cost):
        model.cost_accounting = new_cost
        model.save()
    if lastcost and old_cost.last_costaccounting is not None:
        invoice_changecost_model(new_cost, lastcost=True, old_cost=old_cost.last_costaccounting)
    if not lastcost and old_cost.next_costaccounting.first() is not None:
        invoice_changecost_model(new_cost, lastcost=False, old_cost=old_cost.next_costaccounting.first())


@Signal.decorate('delete_fiscalyear')
def invoice_deleteyear(year):
    for bill in Bill.objects.filter(entry__year=year):
        bill.delete()
    for bill in Bill.objects.filter(Q(date__gte=year.begin) & Q(date__lte=year.end)):
        bill.delete()


@Signal.decorate('check_report')
def check_report_invoice(year):
    for bill in Bill.objects.filter(fiscal_year=year, bill_type__in=(Bill.BILLTYPE_BILL, Bill.BILLTYPE_ASSET, Bill.BILLTYPE_RECEIPT), status__in=(Bill.STATUS_VALID, Bill.STATUS_ARCHIVE)):
        bill.get_saved_pdfreport(False)


def convert_asset_and_revenue():
    nb_correct = 0
    for bill in Bill.objects.filter(Q(bill_type__in=(Bill.BILLTYPE_QUOTATION, Bill.BILLTYPE_ASSET)) & Q(is_revenu=True)):
        bill.is_revenu = bill.payoff_is_revenu()
        bill.save()
        nb_correct += 1
    if nb_correct > 0:
        getLogger("diacamma.invoice").info(" * asset & revenue correction = %d", nb_correct)
        correct_quotation_asset_account()


@Signal.decorate('checkparam')
def invoice_checkparam():
    Parameter.check_and_create(name='invoice-default-sell-account', typeparam=Parameter.TYPE_STRING, title=_("invoice-default-sell-account"),
                               args="{'Multi':False}", value='', meta='("accounting","ChartsAccount", Q(type_of_account=3) & Q(year__is_actif=True), "code", True)')
    Parameter.check_and_create(name='invoice-reduce-account', typeparam=Parameter.TYPE_STRING, title=_("invoice-reduce-account"),
                               args="{'Multi':False}", value='', meta='("accounting","ChartsAccount", Q(type_of_account=3) & Q(year__is_actif=True), "code", True)')
    Parameter.check_and_create(name='invoice-vat-mode', typeparam=Parameter.TYPE_SELECT, title=_("invoice-vat-mode"),
                               args="{'Enum':3}", value='0', param_titles=(_("invoice-vat-mode.0"), _("invoice-vat-mode.1"), _("invoice-vat-mode.2")))
    Parameter.check_and_create(name="invoice-account-third", typeparam=Parameter.TYPE_STRING, title=_("invoice-account-third"),
                               args="{'Multi':False}", value='',
                               meta='("accounting","ChartsAccount","import diacamma.accounting.tools;django.db.models.Q(code__regex=diacamma.accounting.tools.current_system_account().get_customer_mask()) & django.db.models.Q(year__is_actif=True)", "code", True)')
    Parameter.check_and_create(name='invoice-article-with-picture', typeparam=Parameter.TYPE_BOOL, title=_("invoice-article-with-picture"), args="{}", value='False')
    Parameter.check_and_create(name='invoice-custom-field-in-bill', typeparam=Parameter.TYPE_BOOL, title=_("invoice-custom-field-in-bill"), args="{}", value='True')
    Parameter.check_and_create(name='invoice-custom-field-in-array', typeparam=Parameter.TYPE_STRING, title=_("invoice-custom-field-in-array"), args="{'Multi':False}", value='')
    Parameter.check_and_create(name='invoice-reduce-with-ratio', typeparam=Parameter.TYPE_BOOL, title=_("invoice-reduce-with-ratio"), args="{}", value='True')
    Parameter.check_and_create(name='invoice-reduce-allow-article-empty', typeparam=Parameter.TYPE_BOOL, title=_("invoice-reduce-allow-article-empty"), args="{}", value='True')
    Parameter.check_and_create(name='invoice-order-mode', typeparam=Parameter.TYPE_SELECT, title=_("invoice-order-mode"),
                               args="{'Enum':3}", value='0', param_titles=(_("invoice-order-mode.0"), _("invoice-order-mode.1"), _("invoice-order-mode.2")))
    Parameter.check_and_create(name='invoice-asset-mode', typeparam=Parameter.TYPE_SELECT, title=_("invoice-asset-mode"),
                               args="{'Enum':2}", value='0', param_titles=(_("invoice-asset-mode.0"), _("invoice-asset-mode.1")))
    Parameter.check_and_create(name='invoice-default-nbpayoff', typeparam=Parameter.TYPE_INTEGER, title=_("invoice-default-nbpayoff"),
                               args='{"Min":0,"Max":5}', value='0')
    Parameter.check_and_create(name='invoice-default-send-pdf', typeparam=Parameter.TYPE_BOOL, title=_("invoice-default-send-pdf"), args='{}', value='False')

    Parameter.check_and_create(name='invoice-cart-active', typeparam=Parameter.TYPE_BOOL, title=_("invoice-cart-active"), args='{}', value='False')
    Parameter.check_and_create(name='invoice-cart-article-filter', typeparam=Parameter.TYPE_INTEGER, title=_("invoice-cart-article-filter"), args="{}", value='',
                               meta='("CORE","SavedCriteria","django.db.models.Q(modelname=\'%s\')", "id", False)' % Article.get_long_name())
    Parameter.check_and_create(name='invoice-cart-default-category', typeparam=Parameter.TYPE_INTEGER, title=_("invoice-cart-default-category"), args="{}", value='',
                               meta='("invoice","Category","django.db.models.Q()", "id", False)')
    Parameter.check_and_create(name='invoice-cart-timeout', typeparam=Parameter.TYPE_INTEGER, title=_("invoice-cart-timeout"), args='{"Min":0,"Max":99}', value='0')
    Parameter.check_and_create(name='invoice-cart-email-subject', typeparam=Parameter.TYPE_STRING, title=_("invoice-cart-email-subject"), args='{}', value=_('new validated cart'))
    Parameter.check_and_create(name='invoice-cart-email-body', typeparam=Parameter.TYPE_STRING, title=_("invoice-cart-email-body"), args="{'Multi':True, 'HyperText': True}",
                               value=_('#name{[br/]}{[br/]}Joint in this email #doc.{[br/]}#nb quotation is created, each storage area manager will return you them soon.{[br/]}{[br/]}Regards'))
    Parameter.check_and_create(name='invoice-cart-default-comment', typeparam=Parameter.TYPE_STRING, title=_("invoice-cart-default-comment"), args="{'Multi':True, 'HyperText': True}", value='')

    LucteriosGroup.redefine_generic(_("# invoice (administrator)"), Vat.get_permission(True, True, True), BankAccount.get_permission(True, True, True), BankTransaction.get_permission(True, True, True),
                                    Article.get_permission(True, True, True), Bill.get_permission(True, True, True),
                                    StorageSheet.get_permission(True, True, True), Payoff.get_permission(True, True, True), DepositSlip.get_permission(True, True, True))
    LucteriosGroup.redefine_generic(_("# invoice (editor)"), Article.get_permission(True, True, False), Bill.get_permission(True, True, False),
                                    StorageSheet.get_permission(True, True, False), Payoff.get_permission(True, True, True), DepositSlip.get_permission(True, True, False))
    LucteriosGroup.redefine_generic(_("# invoice (shower)"), Article.get_permission(True, False, False), Bill.get_permission(True, False, False),
                                    StorageSheet.get_permission(True, False, False), Payoff.get_permission(True, False, False), DepositSlip.get_permission(True, False, False))

    Preference.check_and_create(name="invoice-status", typeparam=Preference.TYPE_INTEGER, title=_("invoice-status"),
                                args="{'Multi':False}", value=Bill.STATUS_BUILDING_VALID, meta='("","","%s","",False)' % (Bill.SELECTION_STATUS,))
    Preference.check_and_create(name="invoice-billtype", typeparam=Preference.TYPE_STRING, title=_("invoice-billtype"),
                                args="{'Multi':False}", value=Bill.BILLTYPE_ALL, meta='("","","import diacamma.invoice.models;[(str(bill_type), title) for bill_type, title in diacamma.invoice.models.Bill.SELECTION_BILLTYPES]+[(\'%d|%d\' % (cat_bill.id, type_num), \'[%s]%s\' % (cat_bill.name, type_value)) for cat_bill in diacamma.invoice.models.CategoryBill.objects.all() for type_num, _description, type_value in cat_bill.get_title_info()]","",False)')


@Signal.decorate('convertdata')
def invoice_convertdata():
    convert_articles()
    convert_asset_and_revenue()
    correct_db_field({
        'invoice_article': 'price',
        'invoice_detail': 'price',
        'invoice_detail': 'quantity',
        'invoice_detail': 'reduce',
        'invoice_detail': 'vta_rate',
        'invoice_storagedetail': 'price',
    })
    for bill in Bill.objects.filter(status=Bill.STATUS_CANCEL, bill_type__in=(Bill.BILLTYPE_BILL, Bill.BILLTYPE_RECEIPT), entry__isnull=False):
        bill.status = Bill.STATUS_ARCHIVE
        bill.save()


def invoice_addon_for_third():
    for field_name in ["bill_type", "num", "date", "comment", "status"]:
        bill_search = Supporting.convert_field_for_search('bill', (field_name, Bill._meta.get_field(field_name), field_name, Q()))
        yield Third.convert_field_for_search('supporting_set', bill_search, add_verbose=False)


@Signal.decorate('addon_search')
def invoice_addon_search(model, search_result):
    res = False
    if model is Third:
        search_result.extend(invoice_addon_for_third())
        res = True
    if issubclass(model, AbstractContact):
        for subfield in invoice_addon_for_third():
            search_result.append(model.convert_field_for_search('third_set', subfield, add_verbose=False))
    return res


@Signal.decorate('auditlog_register')
def invoice_auditlog_register():
    auditlog.register(Vat, exclude_fields=['ID'])
    auditlog.register(Category, exclude_fields=['ID'])
    auditlog.register(StorageArea, exclude_fields=['ID'])
    auditlog.register(AccountPosting, exclude_fields=['ID'])
    auditlog.register(Provider, exclude_fields=['ID'])
    auditlog.register(AutomaticReduce, include_fields=["name", "category", "mode", "amount_txt", "occurency", "filtercriteria"])
    auditlog.register(Article, include_fields=["reference", "designation", "price", "unit", "accountposting", 'vat', "stockable", "isdisabled", "qtyDecimal"])
    auditlog.register(ArticleCustomField, include_fields=['field', 'data'], mapping_fields=['field'])
    auditlog.register(Bill, include_fields=["bill_type", "status", "num_txt", "date", "third", "comment", "parentbill"])
    auditlog.register(Detail, include_fields=["article", "designation", "price", "unit", "quantity", "storagearea", "reduce"])
    auditlog.register(StorageSheet, include_fields=["sheet_type", "status", "date", "storagearea", "comment", "provider", "bill_date", "bill_reference"])
    auditlog.register(StorageDetail, include_fields=["article", "price", "quantity"])
