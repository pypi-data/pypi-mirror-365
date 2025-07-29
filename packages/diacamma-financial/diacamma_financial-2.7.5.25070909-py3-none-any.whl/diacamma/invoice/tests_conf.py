# -*- coding: utf-8 -*-
'''
diacamma.invoice tests package

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
from shutil import rmtree
from _io import StringIO

from lucterios.framework.test import LucteriosTest
from lucterios.framework.filetools import get_user_dir
from lucterios.CORE.models import SavedCriteria, PrintModel, LucteriosUser
from lucterios.CORE.views import ObjectMerge
from lucterios.CORE.parameters import Params

from diacamma.accounting.test_tools import initial_thirds_fr, default_compta_fr, default_costaccounting, \
    initial_contacts, create_account, create_year
from diacamma.accounting.models import CostAccounting
from diacamma.payoff.test_tools import default_bankaccount_fr, default_paymentmethod
from diacamma.invoice.models import Article, AccountPosting
from diacamma.invoice.test_tools import default_articles, default_categories, default_customize, default_accountPosting, \
    clean_cache, default_multiprice
from diacamma.invoice.views_conf import InvoiceConfFinancial, InvoiceConfCommercial, VatAddModify, VatDel, CategoryAddModify, CategoryDel, ArticleImport, StorageAreaDel, \
    StorageAreaAddModify, AccountPostingAddModify, AccountPostingDel, AutomaticReduceAddModify, AutomaticReduceDel, \
    CategoryBillAddModify, CategoryBillDel, CategoryBillDefault, \
    StorageAreaChangeContact, StorageAreaSaveContact, MultiPriceAddModify, MultiPriceDel
from diacamma.invoice.views import ArticleList, ArticleAddModify, ArticleDel, ArticleShow, ArticleSearch, ArticlePrint, ArticleLabel, \
    RecipeKitArticleAddModify, RecipeKitArticleDel
from base64 import b64decode
from lucterios.contacts.models import Individual


class ConfigTest(LucteriosTest):

    def setUp(self):
        LucteriosTest.setUp(self)
        default_compta_fr()
        default_bankaccount_fr()
        default_paymentmethod()
        clean_cache()
        rmtree(get_user_dir(), True)

    def test_vat(self):
        self.factory.xfer = InvoiceConfFinancial()
        self.calljson('/diacamma.invoice/invoiceConfFinancial', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'invoiceConfFinancial')
        self.assertTrue('__tab_3' in self.json_data.keys(), self.json_data.keys())
        self.assertFalse('__tab_4' in self.json_data.keys(), self.json_data.keys())
        self.assert_count_equal('', 2 + 7 + 2 + 2)  # general + parameters + imputation + vat

        self.assert_grid_equal('vat', {'name': "nom", 'rate': "taux", 'account': "compte de TVA", 'isactif': "actif ?"}, 0)

        self.factory.xfer = VatAddModify()
        self.calljson('/diacamma.invoice/vatAddModify', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'vatAddModify')
        self.assert_count_equal('', 5)

        self.factory.xfer = VatAddModify()
        self.calljson('/diacamma.invoice/vatAddModify',
                      {'name': 'my vat', 'rate': '11.57', 'account': '4455', 'isactif': 1, 'SAVE': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'vatAddModify')

        self.factory.xfer = InvoiceConfFinancial()
        self.calljson('/diacamma.invoice/invoiceConfFinancial', {}, False)
        self.assert_count_equal('vat', 1)
        self.assert_json_equal('', 'vat/@0/name', 'my vat')
        self.assert_json_equal('', 'vat/@0/rate', '11.57')
        self.assert_json_equal('', 'vat/@0/account', '4455')
        self.assert_json_equal('', 'vat/@0/isactif', True)

        self.factory.xfer = VatDel()
        self.calljson('/diacamma.invoice/vatDel', {'vat': 1, 'CONFIRME': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'vatDel')

        self.factory.xfer = InvoiceConfFinancial()
        self.calljson('/diacamma.invoice/invoiceConfFinancial', {}, False)
        self.assert_count_equal('vat', 0)

    def test_category(self):
        self.factory.xfer = InvoiceConfCommercial()
        self.calljson('/diacamma.invoice/invoiceConfCommercial', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'invoiceConfCommercial')
        self.assertTrue('__tab_8' in self.json_data.keys(), self.json_data.keys())
        self.assertFalse('__tab_9' in self.json_data.keys(), self.json_data.keys())
        self.assert_count_equal('', 2 + 10 + 2 + 2 + 2 + 2 + 3 + 2 + 2)

        self.assert_grid_equal('category', {'name': "nom", 'designation': "désignation"}, 0)

        self.factory.xfer = CategoryAddModify()
        self.calljson('/diacamma.invoice/categoryAddModify', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'categoryAddModify')
        self.assert_count_equal('', 3)

        self.factory.xfer = CategoryAddModify()
        self.calljson('/diacamma.invoice/categoryAddModify',
                      {'name': 'my category', 'designation': "bla bla bla", 'SAVE': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'categoryAddModify')

        self.factory.xfer = InvoiceConfCommercial()
        self.calljson('/diacamma.invoice/invoiceConfCommercial', {}, False)
        self.assert_count_equal('category', 1)
        self.assert_json_equal('', 'category/@0/name', 'my category')
        self.assert_json_equal('', 'category/@0/designation', 'bla bla bla')

        self.factory.xfer = CategoryDel()
        self.calljson('/diacamma.invoice/categoryDel', {'category': 1, 'CONFIRME': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'categoryDel')

        self.factory.xfer = InvoiceConfCommercial()
        self.calljson('/diacamma.invoice/invoiceConfCommercial', {}, False)
        self.assert_count_equal('category', 0)

    def test_accountposting(self):
        default_costaccounting()
        create_account(['4191a', '4191b'], 1, None)
        self.factory.xfer = InvoiceConfFinancial()
        self.calljson('/diacamma.invoice/invoiceConfFinancial', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'invoiceConfFinancial')
        self.assert_grid_equal('accountposting', {'name': "nom", 'sell_account': "compte de vente", 'cost_accounting': 'comptabilité analytique'}, 0)

        self.factory.xfer = AccountPostingAddModify()
        self.calljson('/diacamma.invoice/accountPostingAddModify', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'accountPostingAddModify')
        self.assert_count_equal('', 5)
        self.assert_select_equal('sell_account', 3)
        self.assert_select_equal('cost_accounting', {0: None, 2: 'open'})

        self.factory.xfer = AccountPostingAddModify()
        self.calljson('/diacamma.invoice/accountPostingAddModify', {'name': 'aaa', 'sell_account': '701', 'cost_accounting': 2, 'provision_third_account': '4191a', 'SAVE': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'accountPostingAddModify')

        self.factory.xfer = InvoiceConfFinancial()
        self.calljson('/diacamma.invoice/invoiceConfFinancial', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'invoiceConfFinancial')
        self.assert_count_equal('accountposting', 1)

        self.factory.xfer = AccountPostingDel()
        self.calljson('/diacamma.invoice/accountPostingDel', {'accountposting': 1, 'CONFIRME': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'accountPostingDel')

        self.factory.xfer = InvoiceConfFinancial()
        self.calljson('/diacamma.invoice/invoiceConfFinancial', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'invoiceConfFinancial')
        self.assert_count_equal('accountposting', 0)

    def test_accountposting_costaccounting(self):
        year1 = create_year(0, 2021)
        year2 = create_year(0, 2022, year1)
        year3 = create_year(0, 2023, year2)
        cost1 = CostAccounting.objects.create(name='cost 2021', description='cost', status=1, is_default=False, year=year1, last_costaccounting=None)
        cost2 = CostAccounting.objects.create(name='cost 2022', description='cost', status=1, is_default=False, year=year2, last_costaccounting=cost1)
        cost3 = CostAccounting.objects.create(name='cost 2023', description='cost', status=1, is_default=False, year=year3, last_costaccounting=cost2)

        AccountPosting.objects.create(name="my account posting", sell_account='701', cost_accounting=cost3)
        self.factory.xfer = InvoiceConfFinancial()
        self.calljson('/diacamma.invoice/invoiceConfFinancial', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'invoiceConfFinancial')
        self.assert_count_equal('accountposting', 1)
        self.assert_json_equal('', 'accountposting/@0/name', 'my account posting')
        self.assert_json_equal('', 'accountposting/@0/cost_accounting', 'cost 2023')

        year2.set_has_actif()
        self.factory.xfer = InvoiceConfFinancial()
        self.calljson('/diacamma.invoice/invoiceConfFinancial', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'invoiceConfFinancial')
        self.assert_count_equal('accountposting', 1)
        self.assert_json_equal('', 'accountposting/@0/name', 'my account posting')
        self.assert_json_equal('', 'accountposting/@0/cost_accounting', 'cost 2022')

        year1.set_has_actif()
        self.factory.xfer = InvoiceConfFinancial()
        self.calljson('/diacamma.invoice/invoiceConfFinancial', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'invoiceConfFinancial')
        self.assert_count_equal('accountposting', 1)
        self.assert_json_equal('', 'accountposting/@0/name', 'my account posting')
        self.assert_json_equal('', 'accountposting/@0/cost_accounting', 'cost 2021')

        year3.set_has_actif()
        self.factory.xfer = InvoiceConfFinancial()
        self.calljson('/diacamma.invoice/invoiceConfFinancial', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'invoiceConfFinancial')
        self.assert_count_equal('accountposting', 1)
        self.assert_json_equal('', 'accountposting/@0/name', 'my account posting')
        self.assert_json_equal('', 'accountposting/@0/cost_accounting', 'cost 2023')

        year1.set_has_actif()
        self.factory.xfer = InvoiceConfFinancial()
        self.calljson('/diacamma.invoice/invoiceConfFinancial', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'invoiceConfFinancial')
        self.assert_count_equal('accountposting', 1)
        self.assert_json_equal('', 'accountposting/@0/name', 'my account posting')
        self.assert_json_equal('', 'accountposting/@0/cost_accounting', 'cost 2021')

    def test_automaticreduce(self):
        default_categories()
        SavedCriteria.objects.create(name='my filter', modelname='accounting.Third', criteria='azerty')
        SavedCriteria.objects.create(name='other filter', modelname='contacts.EntityLegal', criteria='qwerty')

        self.factory.xfer = InvoiceConfCommercial()
        self.calljson('/diacamma.invoice/invoiceConfCommercial', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'invoiceConfCommercial')
        self.assert_grid_equal('automaticreduce', {'name': "nom", 'category': "catégorie", 'mode': 'mode', 'amount_txt': 'montant', 'occurency': 'occurence', 'filtercriteria': 'critère de filtre'}, 0)

        self.factory.xfer = AutomaticReduceAddModify()
        self.calljson('/diacamma.invoice/automaticReduceAddModify', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'automaticReduceAddModify')
        self.assert_count_equal('', 7)
        self.assert_select_equal('category', 3)
        self.assert_select_equal('filtercriteria', {0: None, 1: 'my filter'})

        self.factory.xfer = AutomaticReduceAddModify()
        self.calljson('/diacamma.invoice/automaticReduceAddModify', {'name': "abc", 'category': 2, 'mode': 1, 'amount': '10.0', 'filtercriteria': '1', 'SAVE': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'automaticReduceAddModify')

        self.factory.xfer = InvoiceConfCommercial()
        self.calljson('/diacamma.invoice/invoiceConfCommercial', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'invoiceConfCommercial')
        self.assert_count_equal('automaticreduce', 1)

        self.factory.xfer = AutomaticReduceDel()
        self.calljson('/diacamma.invoice/automaticReduceDel', {'automaticreduce': 1, 'CONFIRME': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'automaticReduceDel')

        self.factory.xfer = InvoiceConfCommercial()
        self.calljson('/diacamma.invoice/invoiceConfCommercial', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'invoiceConfCommercial')
        self.assert_count_equal('automaticreduce', 0)

    def test_multiprice(self):
        default_categories()
        SavedCriteria.objects.create(name='my filter', modelname='accounting.Third', criteria='azerty')
        SavedCriteria.objects.create(name='other filter', modelname='contacts.EntityLegal', criteria='qwerty')

        self.factory.xfer = InvoiceConfCommercial()
        self.calljson('/diacamma.invoice/invoiceConfCommercial', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'invoiceConfCommercial')
        self.assert_grid_equal('multiprice', {'name': "nom", 'filtercriteria': 'critère de filtre'}, 0)

        self.factory.xfer = MultiPriceAddModify()
        self.calljson('/diacamma.invoice/multiPriceAddModify', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'multiPriceAddModify')
        self.assert_count_equal('', 3)
        self.assert_select_equal('filtercriteria', {0: None, 1: 'my filter'})

        self.factory.xfer = MultiPriceAddModify()
        self.calljson('/diacamma.invoice/multiPriceAddModify', {'name': "abc", 'filtercriteria': '1', 'SAVE': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'multiPriceAddModify')

        self.factory.xfer = InvoiceConfCommercial()
        self.calljson('/diacamma.invoice/invoiceConfCommercial', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'invoiceConfCommercial')
        self.assert_count_equal('multiprice', 1)

        self.factory.xfer = MultiPriceDel()
        self.calljson('/diacamma.invoice/multiPriceDel', {'multiprice': 1, 'CONFIRME': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'multiPriceDel')

        self.factory.xfer = InvoiceConfCommercial()
        self.calljson('/diacamma.invoice/invoiceConfCommercial', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'invoiceConfCommercial')
        self.assert_count_equal('multiprice', 0)

    def test_customize(self):
        default_customize()
        self.factory.xfer = InvoiceConfCommercial()
        self.calljson('/diacamma.invoice/invoiceConfCommercial', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'invoiceConfCommercial')
        self.assertTrue('__tab_8' in self.json_data.keys(), self.json_data.keys())
        self.assertFalse('__tab_9' in self.json_data.keys(), self.json_data.keys())
        self.assert_count_equal('', 2 + 10 + 2 + 2 + 2 + 2 + 3 + 2 + 2)

        self.assert_grid_equal('custom_field', {'name': "nom", 'kind_txt': "type"}, 2)
        self.assert_json_equal('', 'custom_field/@0/name', 'couleur')
        self.assert_json_equal('', 'custom_field/@0/kind_txt', 'Sélection (---,noir,blanc,rouge,bleu,jaune)')
        self.assert_json_equal('', 'custom_field/@1/name', 'taille')
        self.assert_json_equal('', 'custom_field/@1/kind_txt', 'Entier [0;100]')

    def test_storagearea(self):
        initial_contacts()
        self.factory.xfer = InvoiceConfCommercial()
        self.calljson('/diacamma.invoice/invoiceConfCommercial', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'invoiceConfCommercial')
        self.assertTrue('__tab_8' in self.json_data.keys(), self.json_data.keys())
        self.assertFalse('__tab_9' in self.json_data.keys(), self.json_data.keys())
        self.assert_count_equal('', 2 + 10 + 2 + 2 + 2 + 2 + 3 + 2 + 2)

        self.assert_grid_equal('storagearea', {'name': "nom", 'designation': "désignation", 'contact': "gestionnaire"}, 0)

        self.factory.xfer = StorageAreaAddModify()
        self.calljson('/diacamma.invoice/storageAreaAddModify', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'storageAreaAddModify')
        self.assert_count_equal('', 5)

        self.factory.xfer = StorageAreaAddModify()
        self.calljson('/diacamma.invoice/storageAreaAddModify',
                      {'name': 'my category', 'designation': "bla bla bla", 'SAVE': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'storageAreaAddModify')

        self.factory.xfer = InvoiceConfCommercial()
        self.calljson('/diacamma.invoice/invoiceConfCommercial', {}, False)
        self.assert_count_equal('storagearea', 1)
        self.assert_json_equal('', 'storagearea/@0/name', 'my category')
        self.assert_json_equal('', 'storagearea/@0/designation', 'bla bla bla')
        self.assert_json_equal('', 'storagearea/@0/contact', None)

        self.factory.xfer = StorageAreaChangeContact()
        self.calljson('/diacamma.invoice/storageAreaChangeContact', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'storageAreaChangeContact')
        self.assert_count_equal('individual', 5)

        self.factory.xfer = StorageAreaSaveContact()
        self.calljson('/diacamma.invoice/storageAreaSaveContact', {'storagearea': 1, 'individual': 6}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'storageAreaSaveContact')

        self.factory.xfer = InvoiceConfCommercial()
        self.calljson('/diacamma.invoice/invoiceConfCommercial', {}, False)
        self.assert_count_equal('storagearea', 1)
        self.assert_json_equal('', 'storagearea/@0/name', 'my category')
        self.assert_json_equal('', 'storagearea/@0/designation', 'bla bla bla')
        self.assert_json_equal('', 'storagearea/@0/contact', 'Luke Lucky')

        self.factory.xfer = StorageAreaDel()
        self.calljson('/diacamma.invoice/storageAreaDel', {'storagearea': 1, 'CONFIRME': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'storageAreaDel')

        self.factory.xfer = InvoiceConfCommercial()
        self.calljson('/diacamma.invoice/invoiceConfCommercial', {}, False)
        self.assert_count_equal('storagearea', 0)

    def test_catogoriesbill(self):
        Params.setvalue('invoice-order-mode', 1)
        Params.setvalue('invoice-cart-active', True)
        self.factory.xfer = InvoiceConfCommercial()
        self.calljson('/diacamma.invoice/invoiceConfCommercial', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'invoiceConfCommercial')
        self.assertTrue('__tab_8' in self.json_data.keys(), self.json_data.keys())
        self.assertFalse('__tab_9' in self.json_data.keys(), self.json_data.keys())
        self.assert_count_equal('', 2 + 9 + 2 + 2 + 2 + 2 + 10 + 2 + 2)

        self.assert_grid_equal('categoryBill', {'name': "nom", 'designation': "désignation", "titles_txt": "titres", "is_default": "défaut"}, 0)

        self.factory.xfer = CategoryBillAddModify()
        self.calljson('/diacamma.invoice/categoryBillAddModify', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'categoryBillAddModify')
        self.assert_count_equal('', 18)
        self.assert_json_equal('EDIT', 'title_5', "panier")
        self.assert_json_equal('EDIT', 'title_0', "devis")
        self.assert_json_equal('EDIT', 'title_4', "commande")
        self.assert_json_equal('EDIT', 'title_1', "facture")
        self.assert_json_equal('EDIT', 'title_2', "avoir")
        self.assert_json_equal('SELECT', 'printmodel', 0)
        self.assert_select_equal('printmodel', {0: None, 8: 'facture', 9: 'règlement'})
        self.assert_json_equal('SELECT', 'printmodel_sold', 0)
        self.assert_select_equal('printmodel_sold', {0: None, 8: 'facture', 9: 'règlement'})
        self.assert_json_equal('CHECK', 'special_numbering', False)
        self.assert_json_equal('EDIT', 'prefix_numbering', '')
        self.assert_json_equal('SELECT', 'workflow_order', 0)
        self.assert_select_equal('workflow_order', {0: 'avec ou sans commande', 1: 'toujours avec commande', 2: 'jamais avec commande'})
        self.assert_json_equal('CHECKLIST', 'payment_method', [])
        self.assert_select_equal('payment_method', 6, checked=True)
        self.assert_json_equal('CHECK', 'with_multi_emailinfo', False)
        self.assert_json_equal('EDIT', 'emailsubject', "#reference")
        self.assert_json_equal('MEMO', 'emailmessage', "#name{[br/]}{[br/]}Veuillez trouver joint à ce courriel #doc.{[br/]}{[br/]}Sincères salutations")

        self.factory.xfer = CategoryBillAddModify()
        self.calljson('/diacamma.invoice/categoryBillAddModify', {'workflow_order': 2}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'categoryBillAddModify')
        self.assert_count_equal('', 17)
        self.assert_json_equal('EDIT', 'title_5', "panier")
        self.assert_json_equal('EDIT', 'title_0', "devis")
        self.assert_json_equal('EDIT', 'title_1', "facture")
        self.assert_json_equal('EDIT', 'title_2', "avoir")
        self.assert_json_equal('SELECT', 'printmodel', 0)
        self.assert_select_equal('printmodel', {0: None, 8: 'facture', 9: 'règlement'})
        self.assert_json_equal('SELECT', 'printmodel_sold', 0)
        self.assert_select_equal('printmodel_sold', {0: None, 8: 'facture', 9: 'règlement'})
        self.assert_json_equal('CHECK', 'special_numbering', False)
        self.assert_json_equal('EDIT', 'prefix_numbering', '')
        self.assert_json_equal('SELECT', 'workflow_order', 2)
        self.assert_json_equal('CHECKLIST', 'payment_method', [])
        self.assert_json_equal('CHECK', 'with_multi_emailinfo', False)
        self.assert_json_equal('EDIT', 'emailsubject', "#reference")
        self.assert_json_equal('MEMO', 'emailmessage', "#name{[br/]}{[br/]}Veuillez trouver joint à ce courriel #doc.{[br/]}{[br/]}Sincères salutations")

        self.factory.xfer = CategoryBillAddModify()
        self.calljson('/diacamma.invoice/categoryBillAddModify', {'with_multi_emailinfo': True}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'categoryBillAddModify')
        self.assert_count_equal('', 28)
        self.assert_json_equal('EDIT', 'title_5', "panier")
        self.assert_json_equal('EDIT', 'title_0', "devis")
        self.assert_json_equal('EDIT', 'title_4', "commande")
        self.assert_json_equal('EDIT', 'title_1', "facture")
        self.assert_json_equal('EDIT', 'title_2', "avoir")
        self.assert_json_equal('SELECT', 'printmodel', 0)
        self.assert_select_equal('printmodel', {0: None, 8: 'facture', 9: 'règlement'})
        self.assert_json_equal('SELECT', 'printmodel_sold', 0)
        self.assert_select_equal('printmodel_sold', {0: None, 8: 'facture', 9: 'règlement'})
        self.assert_json_equal('CHECK', 'special_numbering', False)
        self.assert_json_equal('EDIT', 'prefix_numbering', '')
        self.assert_json_equal('SELECT', 'workflow_order', 0)
        self.assert_select_equal('workflow_order', {0: 'avec ou sans commande', 1: 'toujours avec commande', 2: 'jamais avec commande'})
        self.assert_json_equal('CHECKLIST', 'payment_method', [])
        self.assert_select_equal('payment_method', 6, checked=True)
        self.assert_json_equal('CHECK', 'with_multi_emailinfo', True)
        self.assert_json_equal('EDIT', 'emailsubject_0', "#reference")
        self.assert_json_equal('MEMO', 'emailmessage_0', "#name{[br/]}{[br/]}Veuillez trouver joint à ce courriel #doc.{[br/]}{[br/]}Sincères salutations")
        self.assert_json_equal('EDIT', 'emailsubject_4', "#reference")
        self.assert_json_equal('MEMO', 'emailmessage_4', "#name{[br/]}{[br/]}Veuillez trouver joint à ce courriel #doc.{[br/]}{[br/]}Sincères salutations")
        self.assert_json_equal('EDIT', 'emailsubject_1', "#reference")
        self.assert_json_equal('MEMO', 'emailmessage_1', "#name{[br/]}{[br/]}Veuillez trouver joint à ce courriel #doc.{[br/]}{[br/]}Sincères salutations")
        self.assert_json_equal('EDIT', 'emailsubject_2', "#reference")
        self.assert_json_equal('MEMO', 'emailmessage_2', "#name{[br/]}{[br/]}Veuillez trouver joint à ce courriel #doc.{[br/]}{[br/]}Sincères salutations")

        self.factory.xfer = CategoryBillAddModify()
        self.calljson('/diacamma.invoice/categoryBillAddModify',
                      {'name': 'cat1', 'designation': "Truc", 'special_numbering': False, 'prefix_numbering': '', 'workflow_order': 2,
                       'title_0': 'AAA', 'title_1': 'BBB', 'title_2': 'CCC', 'title_5': 'DDD', 'is_default': 1,
                       'emailsubject': "#reference", 'emailmessage': "Hello", 'printmodel': 8, 'printmodel_sold': 9, 'payment_method': '1;2;3;4',
                       'SAVE': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'categoryBillAddModify')

        self.factory.xfer = CategoryBillAddModify()
        self.calljson('/diacamma.invoice/categoryBillAddModify',
                      {'name': 'cat2', 'designation': "Machin", 'special_numbering': True, 'prefix_numbering': 'Mc', 'workflow_order': 0,
                       'title_0': 'ZZZ', 'title_1': 'YYY', 'title_2': 'XXX', 'title_4': 'VVV', 'is_default': 0,
                       'emailsubject': "#reference", 'emailmessage': "Hello", 'printmodel': 9, 'printmodel_sold': 8, 'payment_method': '1;2;3;5;6',
                       'SAVE': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'categoryBillAddModify')

        self.factory.xfer = InvoiceConfCommercial()
        self.calljson('/diacamma.invoice/invoiceConfCommercial', {}, False)
        self.assert_count_equal('categoryBill', 2)
        self.assert_json_equal('', 'categoryBill/@0/name', 'cat1')
        self.assert_json_equal('', 'categoryBill/@0/designation', 'Truc')
        self.assert_json_equal('', 'categoryBill/@0/titles_txt', ["titre pour 'panier' = DDD", "titre pour 'devis' = AAA", "titre pour 'facture' = BBB", "titre pour 'avoir' = CCC"])
        self.assert_json_equal('', 'categoryBill/@0/is_default', True)
        self.assert_json_equal('', 'categoryBill/@1/name', 'cat2')
        self.assert_json_equal('', 'categoryBill/@1/designation', 'Machin')
        self.assert_json_equal('', 'categoryBill/@1/titles_txt', ["titre pour 'devis' = ZZZ", "titre pour 'commande' = VVV", "titre pour 'facture' = YYY", "titre pour 'avoir' = XXX"])
        self.assert_json_equal('', 'categoryBill/@1/is_default', False)

        self.factory.xfer = CategoryBillDefault()
        self.calljson('/diacamma.invoice/categoryBillDefault', {'categoryBill': 2}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'categoryBillDefault')
        self.factory.xfer = InvoiceConfCommercial()
        self.calljson('/diacamma.invoice/invoiceConfCommercial', {}, False)
        self.assert_count_equal('categoryBill', 2)
        self.assert_json_equal('', 'categoryBill/@0/name', 'cat1')
        self.assert_json_equal('', 'categoryBill/@0/is_default', False)
        self.assert_json_equal('', 'categoryBill/@1/name', 'cat2')
        self.assert_json_equal('', 'categoryBill/@1/is_default', True)

        self.factory.xfer = CategoryBillDefault()
        self.calljson('/diacamma.invoice/categoryBillDefault', {'categoryBill': 1}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'categoryBillDefault')
        self.factory.xfer = InvoiceConfCommercial()
        self.calljson('/diacamma.invoice/invoiceConfCommercial', {}, False)
        self.assert_count_equal('categoryBill', 2)
        self.assert_json_equal('', 'categoryBill/@0/name', 'cat1')
        self.assert_json_equal('', 'categoryBill/@0/is_default', True)
        self.assert_json_equal('', 'categoryBill/@1/name', 'cat2')
        self.assert_json_equal('', 'categoryBill/@1/is_default', False)

        self.factory.xfer = CategoryBillDefault()
        self.calljson('/diacamma.invoice/categoryBillDefault', {'categoryBill': 1}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'categoryBillDefault')
        self.factory.xfer = InvoiceConfCommercial()
        self.calljson('/diacamma.invoice/invoiceConfCommercial', {}, False)
        self.assert_count_equal('categoryBill', 2)
        self.assert_json_equal('', 'categoryBill/@0/name', 'cat1')
        self.assert_json_equal('', 'categoryBill/@0/is_default', False)
        self.assert_json_equal('', 'categoryBill/@1/name', 'cat2')
        self.assert_json_equal('', 'categoryBill/@1/is_default', False)

        self.factory.xfer = CategoryBillDel()
        self.calljson('/diacamma.invoice/categoryBillDel', {'categoryBill': 1, 'CONFIRME': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'categoryBillDel')

        self.factory.xfer = InvoiceConfCommercial()
        self.calljson('/diacamma.invoice/invoiceConfCommercial', {}, False)
        self.assert_count_equal('categoryBill', 1)

    def test_article(self):
        default_accountPosting()
        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('', 6)
        self.assert_select_equal('stockable', 7)
        self.assert_grid_equal('article', {'reference': "référence", 'designation': "désignation", 'price': "prix", 'unit': "unité", 'stockable': "stockable"}, 0)
        self.assert_count_equal('#article/actions', 3)

        self.factory.xfer = ArticleAddModify()
        self.calljson('/diacamma.invoice/articleAddModify', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleAddModify')
        self.assert_count_equal('', 11)
        self.assert_json_equal('EDIT', 'reference', '')
        self.assert_json_equal('MEMO', 'designation', '')
        self.assert_json_equal('FLOAT', 'price', 0.0)
        self.assert_json_equal('SELECT', 'accountposting', 0)
        self.assert_json_equal('SELECT', 'stockable', '0')
        self.assert_json_equal('FLOAT', 'qtyDecimal', '0')

        self.factory.xfer = ArticleAddModify()
        self.calljson('/diacamma.invoice/articleAddModify',
                      {'reference': 'ABC001', 'designation': 'My beautiful article', 'price': '43.72', 'accountposting': 4, 'stockable': '1', 'qtyDecimal': '1', 'SAVE': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'articleAddModify')

        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('article', 1)
        self.assert_json_equal('', 'article/@0/reference', "ABC001")
        self.assert_json_equal('', 'article/@0/designation', "My beautiful article")
        self.assert_json_equal('', 'article/@0/price', 43.72)
        self.assert_json_equal('', 'article/@0/unit', '')
        self.assert_json_equal('', 'article/@0/stockable', 1)

        self.factory.xfer = ArticleShow()
        self.calljson('/diacamma.invoice/articleShow', {'article': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleShow')
        self.assert_count_equal('', 15)
        self.assert_json_equal('', 'reference', 'ABC001')
        self.assert_json_equal('', 'designation', 'My beautiful article')
        self.assert_json_equal('', 'price', 43.72)
        self.assert_json_equal('', 'accountposting', "code4")
        self.assert_json_equal('', 'stockable', '1')
        self.assert_json_equal('', 'qtyDecimal', '1')

        self.factory.xfer = ArticleDel()
        self.calljson('/diacamma.invoice/articleDel',
                      {'article': '1', 'CONFIRME': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'articleDel')

        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('article', 0)

        self.factory.xfer = ArticlePrint()
        self.calljson('/diacamma.invoice/articlePrint', {"MODEL": 11, "PRINT_MODE": 3}, False)
        self.assert_observer('core.print', 'diacamma.invoice', 'articlePrint')
        self.save_pdf()

        self.factory.xfer = ArticleLabel()
        self.calljson('/diacamma.invoice/articleLabel', {"LABEL": 1, "FIRSTLABEL": 1, "MODEL": 12, "PRINT_MODE": 3}, False)
        self.assert_observer('core.print', 'diacamma.invoice', 'articleLabel')
        self.save_pdf()

    def test_article_with_cat(self):
        default_categories()
        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('', 7)
        self.assert_select_equal("cat_filter", 3, True)
        self.assert_grid_equal('article', {"reference": "référence", "designation": "désignation", "price": "prix", "unit": "unité",
                                           "stockable": "stockable", "categories": "catégories"}, 0)

        self.factory.xfer = ArticleAddModify()
        self.calljson('/diacamma.invoice/articleAddModify', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleAddModify')
        self.assert_count_equal('', 13)

        self.factory.xfer = ArticleAddModify()
        self.calljson('/diacamma.invoice/articleAddModify',
                      {'reference': 'ABC001', 'designation': 'My beautiful article', 'price': '43.72', 'sell_account': '705', 'stockable': '1', 'categories': '2;3', 'SAVE': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'articleAddModify')

        self.factory.xfer = ArticleShow()
        self.calljson('/diacamma.invoice/articleShow', {'article': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleShow')
        self.assert_count_equal('', 16)
        self.assert_json_equal('', 'qtyDecimal', '0')

        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('article', 1)
        self.assert_json_equal('', 'article/@0/categories', ["cat 2", "cat 3"])

    def test_article_merge(self):
        default_categories()
        default_articles(with_storage=True)
        default_customize()
        initial_thirds_fr()

        search_field_list = Article.get_search_fields()
        self.assertEqual(8 + 2 + 3 + 2 + 1, len(search_field_list), search_field_list)  # article + art custom + category + provider

        self.factory.xfer = ArticleSearch()
        self.calljson('/diacamma.invoice/articleSearch', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleSearch')
        self.assert_count_equal('article', 5)
        self.assert_json_equal('', 'article/@0/reference', "ABC1")
        self.assert_json_equal('', 'article/@1/reference', "ABC2")
        self.assert_json_equal('', 'article/@2/reference', "ABC3")
        self.assert_json_equal('', 'article/@3/reference', "ABC4")
        self.assert_json_equal('', 'article/@4/reference', "ABC5")
        self.assert_json_equal('', 'article/@0/categories', ["cat 1"])
        self.assert_json_equal('', 'article/@1/categories', ["cat 2"])
        self.assert_json_equal('', 'article/@2/categories', ["cat 2", "cat 3"])
        self.assert_json_equal('', 'article/@3/categories', ["cat 3"])
        self.assert_json_equal('', 'article/@4/categories', ["cat 1", "cat 2", "cat 3"])
        self.assert_count_equal('#article/actions', 4)
        self.assert_action_equal('POST', '#article/actions/@3', ('Fusion', 'mdi:mdi-set-merge', 'CORE', 'objectMerge', 0, 1, 2,
                                                                 {'modelname': 'invoice.Article', 'field_id': 'article'}))

        self.factory.xfer = ObjectMerge()
        self.calljson('/CORE/objectMerge', {'modelname': 'invoice.Article', 'field_id': 'article', 'article': '1;3;5'}, False)
        self.assert_observer('core.custom', 'CORE', 'objectMerge')
        self.assert_count_equal('mrg_object', 3)
        self.assert_json_equal('', 'mrg_object/@0/value', "ABC1")
        self.assert_json_equal('', 'mrg_object/@1/value', "ABC3")
        self.assert_json_equal('', 'mrg_object/@2/value', "ABC5")

        self.factory.xfer = ObjectMerge()
        self.calljson('/CORE/objectMerge', {'modelname': 'invoice.Article', 'field_id': 'article', 'article': '1;3;5', 'CONFIRME': 'YES', 'mrg_object': '3'}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'objectMerge')
        self.assert_action_equal('GET', self.response_json['action'], ('Editer', 'mdi:mdi-text-box-outline', 'diacamma.invoice', 'articleShow', 1, 1, 1, {'article': '3'}))

        self.factory.xfer = ArticleSearch()
        self.calljson('/diacamma.invoice/articleSearch', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleSearch')
        self.assert_count_equal('article', 3)
        self.assert_json_equal('', 'article/@0/reference', "ABC2")
        self.assert_json_equal('', 'article/@1/reference', "ABC3")
        self.assert_json_equal('', 'article/@2/reference', "ABC4")
        self.assert_json_equal('', 'article/@0/categories', ["cat 2"])
        self.assert_json_equal('', 'article/@1/categories', ["cat 1", "cat 2", "cat 3"])
        self.assert_json_equal('', 'article/@2/categories', ["cat 3"])

    def test_article_filter(self):
        default_categories()
        default_articles(with_storage=True)
        default_customize()
        initial_thirds_fr()

        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('', 7)
        self.assert_count_equal('article', 4)

        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {'show_filter': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('', 7)
        self.assert_count_equal('article', 5)

        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {'show_filter': 1, 'stockable': 0}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('', 7)
        self.assert_count_equal('article', 2)

        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {'show_filter': 1, 'stockable': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('', 7)
        self.assert_count_equal('article', 2)

        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {'show_filter': 1, 'stockable': 2}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('', 7)
        self.assert_count_equal('article', 1)

        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {'show_filter': 1, 'stockable': 3}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('', 7)
        self.assert_count_equal('article', 0)

        self.factory.xfer = ArticlePrint()
        self.calljson('/diacamma.invoice/articlePrint', {'show_filter': 1, 'stockable': 3, "MODEL": 11, "PRINT_MODE": 3}, False)
        self.assert_observer('core.print', 'diacamma.invoice', 'articlePrint')
        self.save_pdf(ident=1)

        self.factory.xfer = ArticleLabel()
        self.calljson('/diacamma.invoice/articleLabel', {'show_filter': 1, 'stockable': 3, "LABEL": 1, "FIRSTLABEL": 1, "MODEL": 12, "PRINT_MODE": 3}, False)
        self.assert_observer('core.print', 'diacamma.invoice', 'articleLabel')
        self.save_pdf(ident=2)

        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {'show_filter': 1, 'cat_filter': '2'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('', 7)
        self.assert_count_equal('article', 3)

        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {'show_filter': 1, 'cat_filter': '2;3'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('', 7)
        self.assert_count_equal('article', 2)

        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {'show_filter': 1, 'cat_filter': '1;2;3'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('', 7)
        self.assert_count_equal('article', 1)

        self.factory.xfer = ArticlePrint()
        self.calljson('/diacamma.invoice/articlePrint', {'show_filter': 1, 'cat_filter': '1;2;3', "MODEL": 11, "PRINT_MODE": 3}, False)
        self.assert_observer('core.print', 'diacamma.invoice', 'articlePrint')
        self.save_pdf(ident=3)

        self.factory.xfer = ArticleLabel()
        self.calljson('/diacamma.invoice/articleLabel', {'show_filter': 1, 'cat_filter': '1;2;3', "LABEL": 1, "FIRSTLABEL": 1, "MODEL": 12, "PRINT_MODE": 3}, False)
        self.assert_observer('core.print', 'diacamma.invoice', 'articleLabel')
        self.save_pdf(ident=4)

    def test_article_import1(self):
        initial_thirds_fr()
        default_categories()
        default_accountPosting()
        csv_content = """'num','comment','prix','unité','compte','stock?','categorie','fournisseur','ref','desactif',
'A123','article N°1','','Kg','code1','stockable','cat 2','Dalton Avrel','POIYT','non',
'B234','article N°2','23,56','L','code1','stockable','cat 3','','','Oui',
'C345','article N°3','45.74','','code2','non stockable','cat 1','Dalton Avrel','MLKJH','yEs',
'D456','article N°4','56,89','m','code1','stockable & non vendable','','Maximum','987654','non',
'A123','article N°1','13.57','Kg','code1','stockable','cat 3','','','non',
'A123','article N°1','16,95','Kg','code1','stockable','','Maximum','654321','non',
"""

        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {'show_filter': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('article', 0)

        self.factory.xfer = ArticleImport()
        self.calljson('/diacamma.invoice/articleImport', {'step': 2, 'modelname': 'invoice.Article', 'quotechar': "'",
                                                          'delimiter': ',', 'encoding': 'utf-8', 'dateformat': '%d/%m/%Y', 'importcontent': StringIO(csv_content)}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleImport')
        self.assert_count_equal('', 7 + 12)
        self.assert_select_equal('fld_reference', 10)  # nb=9
        self.assert_select_equal('fld_categories', 11)  # nb=10
        self.assert_count_equal('Array', 6)
        self.assert_count_equal('#Array/actions', 0)
        self.assertEqual(len(self.json_actions), 1)
        self.assert_action_equal('POST', self.json_actions[0], ('Annuler', 'mdi:mdi-cancel'))
        self.assertEqual(len(self.json_context), 8)

        self.factory.xfer = ArticleImport()
        self.calljson('/diacamma.invoice/articleImport', {'step': 3, 'modelname': 'invoice.Article', 'quotechar': "'", 'delimiter': ',',
                                                          'encoding': 'utf-8', 'dateformat': '%d/%m/%Y', 'importcontent0': csv_content,
                                                          "fld_reference": "num", "fld_designation": "comment", "fld_price": "prix",
                                                          "fld_unit": "unité", "fld_isdisabled": "desactif", "fld_accountposting": "compte",
                                                          "fld_vat": "", "fld_stockable": "stock?", 'fld_categories': 'categorie',
                                                          'fld_provider.third.contact': 'fournisseur', 'fld_provider.reference': 'ref', }, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleImport')
        self.assert_count_equal('', 5)
        self.assert_count_equal('Array', 6)
        self.assert_count_equal('#Array/actions', 0)
        self.assertEqual(len(self.json_actions), 1)
        self.assert_action_equal('POST', self.json_actions[0], ('Annuler', 'mdi:mdi-cancel'))

        self.factory.xfer = ArticleImport()
        self.calljson('/diacamma.invoice/articleImport', {'step': 4, 'modelname': 'invoice.Article', 'quotechar': "'", 'delimiter': ',',
                                                          'encoding': 'utf-8', 'dateformat': '%d/%m/%Y', 'importcontent0': csv_content,
                                                          "fld_reference": "num", "fld_designation": "comment", "fld_price": "prix",
                                                          "fld_unit": "unité", "fld_isdisabled": "desactif", "fld_accountposting": "compte",
                                                          "fld_vat": "", "fld_stockable": "stock?", 'fld_categories': 'categorie',
                                                          'fld_provider.third.contact': 'fournisseur', 'fld_provider.reference': 'ref', }, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleImport')
        self.assert_count_equal('', 3)
        self.assert_json_equal('LABELFORM', 'result', "4 éléments ont été importés")
        self.assert_json_equal('LABELFORM', 'import_error', [])
        self.assert_json_equal('', '#result/formatstr', "{[center]}{[i]}%s{[/i]}{[/center]}")
        self.assertEqual(len(self.json_actions), 1)

        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {'show_filter': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('article', 4)
        self.assert_json_equal('', 'article/@0/reference', "A123")
        self.assert_json_equal('', 'article/@0/designation', "article N°1")
        self.assert_json_equal('', 'article/@0/price', 16.95)
        self.assert_json_equal('', 'article/@0/unit', 'Kg')
        self.assert_json_equal('', 'article/@0/stockable', 1)
        self.assert_json_equal('', 'article/@0/categories', ["cat 2", "cat 3"])

        self.assert_json_equal('', 'article/@1/reference', "B234")
        self.assert_json_equal('', 'article/@1/designation', "article N°2")
        self.assert_json_equal('', 'article/@1/price', 23.56)
        self.assert_json_equal('', 'article/@1/unit', 'L')
        self.assert_json_equal('', 'article/@1/stockable', 1)
        self.assert_json_equal('', 'article/@1/categories', ["cat 3"])

        self.assert_json_equal('', 'article/@2/reference', "C345")
        self.assert_json_equal('', 'article/@2/designation', "article N°3")
        self.assert_json_equal('', 'article/@2/price', 45.74)
        self.assert_json_equal('', 'article/@2/unit', '')
        self.assert_json_equal('', 'article/@2/stockable', 0)
        self.assert_json_equal('', 'article/@2/categories', ["cat 1"])

        self.assert_json_equal('', 'article/@3/reference', "D456")
        self.assert_json_equal('', 'article/@3/designation', "article N°4")
        self.assert_json_equal('', 'article/@3/price', 56.89)
        self.assert_json_equal('', 'article/@3/unit', 'm')
        self.assert_json_equal('', 'article/@3/stockable', 2)
        self.assert_json_equal('', 'article/@3/categories', [])

        self.factory.xfer = ArticleShow()
        self.calljson('/diacamma.invoice/articleShow', {'article': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleShow')
        self.assert_count_equal('', 18)
        self.assert_json_equal('LABELFORM', 'reference', "A123")
        self.assert_json_equal('LABELFORM', 'categories', ["cat 2", "cat 3"])
        self.assert_count_equal('provider', 2)
        self.assert_json_equal('', 'provider/@0/third', "Dalton Avrel")
        self.assert_json_equal('', 'provider/@0/reference', "POIYT")
        self.assert_json_equal('', 'provider/@1/third', "Maximum")
        self.assert_json_equal('', 'provider/@1/reference', "654321")

        self.factory.xfer = ArticleImport()
        self.calljson('/diacamma.invoice/articleImport', {'step': 4, 'modelname': 'invoice.Article', 'quotechar': "'", 'delimiter': ',',
                                                          'encoding': 'utf-8', 'dateformat': '%d/%m/%Y', 'importcontent0': csv_content,
                                                          "fld_reference": "num", "fld_designation": "comment", "fld_price": "prix",
                                                          "fld_unit": "unité", "fld_isdisabled": "desactif", "fld_accountposting": "compte",
                                                          "fld_vat": "", "fld_stockable": "stock?", 'fld_categories': 'categorie',
                                                          'fld_provider.third.contact': 'fournisseur', 'fld_provider.reference': 'ref', }, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleImport')
        self.assert_count_equal('', 3)
        self.assert_json_equal('LABELFORM', 'result', "4 éléments ont été importés")
        self.assert_json_equal('LABELFORM', 'import_error', [])
        self.assertEqual(len(self.json_actions), 1)

        self.factory.xfer = ArticleShow()
        self.calljson('/diacamma.invoice/articleShow', {'article': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleShow')
        self.assert_count_equal('', 18)
        self.assert_json_equal('LABELFORM', 'reference', "A123")
        self.assert_json_equal('LABELFORM', 'categories', ["cat 2", "cat 3"])
        self.assert_count_equal('provider', 2)
        self.assert_json_equal('', 'provider/@0/third', "Dalton Avrel")
        self.assert_json_equal('', 'provider/@0/reference', "POIYT")
        self.assert_json_equal('', 'provider/@1/third', "Maximum")
        self.assert_json_equal('', 'provider/@1/reference', "654321")

    def test_article_import2(self):
        initial_thirds_fr()
        default_categories()
        default_accountPosting()
        csv_content = """'num','comment','prix','unité','compte','stock?','categorie','fournisseur','ref','desactif'
'A123','article N°1','ssdqs','Kg','code1','stockable','cat 2','Avrel','POIYT',0
'B234','article N°2','23.56','L','code1','stockable','cat 3','','',1
'C345','article N°3','45.74','','code2','non stockable','cat 1','Avrel','MLKJH',1
'D456','article N°4','56.89','m','code1','stockable & non vendable','','Maximum','987654',0
'A123','article N°1','13.57','Kg','code1','stockable','cat 3','','',0
'A123','article N°1','16.95','Kg','code1','stockable','','Maximum','654321',0
"""

        self.factory.xfer = ArticleImport()
        self.calljson('/diacamma.invoice/articleImport', {'step': 4, 'modelname': 'invoice.Article', 'quotechar': "'", 'delimiter': ',',
                                                          'encoding': 'utf-8', 'dateformat': '%d/%m/%Y', 'importcontent0': csv_content,
                                                          "fld_reference": "num", "fld_designation": "comment", "fld_price": "prix",
                                                          "fld_unit": "unité", "fld_isdisabled": "desactif", "fld_accountposting": "compte",
                                                          "fld_vat": "", "fld_stockable": "stock?", 'fld_categories': '',
                                                          'fld_provider.third.contact': '', 'fld_provider.reference': '', }, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleImport')
        self.assert_count_equal('', 3)
        self.assert_json_equal('LABELFORM', 'result', "4 éléments ont été importés")
        self.assert_json_equal('LABELFORM', 'import_error', [])
        self.assertEqual(len(self.json_actions), 1)

        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {'show_filter': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('article', 4)
        self.assert_json_equal('', 'article/@0/reference', "A123")
        self.assert_json_equal('', 'article/@0/designation', "article N°1")
        self.assert_json_equal('', 'article/@0/price', 16.95)
        self.assert_json_equal('', 'article/@0/unit', 'Kg')
        self.assert_json_equal('', 'article/@0/stockable', 1)
        self.assert_json_equal('', 'article/@0/categories', [])

        self.assert_json_equal('', 'article/@1/reference', "B234")
        self.assert_json_equal('', 'article/@1/designation', "article N°2")
        self.assert_json_equal('', 'article/@1/price', 23.56)
        self.assert_json_equal('', 'article/@1/unit', 'L')
        self.assert_json_equal('', 'article/@1/stockable', 1)
        self.assert_json_equal('', 'article/@1/categories', [])

        self.assert_json_equal('', 'article/@2/reference', "C345")
        self.assert_json_equal('', 'article/@2/designation', "article N°3")
        self.assert_json_equal('', 'article/@2/price', 45.74)
        self.assert_json_equal('', 'article/@2/unit', '')
        self.assert_json_equal('', 'article/@2/stockable', 0)
        self.assert_json_equal('', 'article/@2/categories', [])

        self.assert_json_equal('', 'article/@3/reference', "D456")
        self.assert_json_equal('', 'article/@3/designation', "article N°4")
        self.assert_json_equal('', 'article/@3/price', 56.89)
        self.assert_json_equal('', 'article/@3/unit', 'm')
        self.assert_json_equal('', 'article/@3/stockable', 2)
        self.assert_json_equal('', 'article/@3/categories', [])

        self.factory.xfer = ArticleShow()
        self.calljson('/diacamma.invoice/articleShow', {'article': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleShow')
        self.assert_count_equal('', 18)
        self.assert_json_equal('LABELFORM', 'reference', "A123")
        self.assert_json_equal('LABELFORM', 'categories', [])
        self.assert_count_equal('provider', 0)

    def test_article_import3(self):
        default_customize()
        default_accountPosting()
        csv_content = """'num','comment','prix','unité','compte','stock?','categorie','fournisseur','ref','color','size','desactif'
'A123','article N°1','12.45','Kg','code1','stockable','cat 2','Avrel','POIYT','---','10','False'
'B234','article N°2','23.56','L','code1','stockable','cat 3','','','noir','25','True'
'C345','article N°3','45.74','','code2','non stockable','cat 1','Avrel','MLKJH','rouge','75','true'
'D456','article N°4','56.89','m','code1','stockable & non vendable','','Maximum','987654','blanc','1','False'
'A123','article N°1','13.57','Kg','code1','stockable','cat 3','','','bleu','10','False'
'A123','article N°1','16.95','Kg','code1','stockable','','Maximum','654321','bleu','15','False'
"""

        self.factory.xfer = ArticleImport()
        self.calljson('/diacamma.invoice/articleImport', {'step': 4, 'modelname': 'invoice.Article', 'quotechar': "'", 'delimiter': ',',
                                                          'encoding': 'utf-8', 'dateformat': '%d/%m/%Y', 'importcontent0': csv_content,
                                                          "fld_reference": "num", "fld_designation": "comment", "fld_price": "prix",
                                                          "fld_unit": "unité", "fld_isdisabled": "desactif", "fld_accountposting": "compte",
                                                          "fld_vat": "", "fld_stockable": "stock?",
                                                          "fld_custom_1": "color", "fld_custom_2": "size", }, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleImport')
        self.assert_count_equal('', 3)
        self.assert_json_equal('LABELFORM', 'result', "4 éléments ont été importés")
        self.assert_json_equal('LABELFORM', 'import_error', [])
        self.assertEqual(len(self.json_actions), 1)

        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {'show_filter': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('article', 4)
        self.assert_json_equal('', 'article/@0/reference', "A123")
        self.assert_json_equal('', 'article/@0/designation', "article N°1")
        self.assert_json_equal('', 'article/@0/price', 16.95)
        self.assert_json_equal('', 'article/@0/unit', 'Kg')
        self.assert_json_equal('', 'article/@0/stockable', 1)

        self.assert_json_equal('', 'article/@1/reference', "B234")
        self.assert_json_equal('', 'article/@1/designation', "article N°2")
        self.assert_json_equal('', 'article/@1/price', 23.56)
        self.assert_json_equal('', 'article/@1/unit', 'L')
        self.assert_json_equal('', 'article/@1/stockable', 1)

        self.assert_json_equal('', 'article/@2/reference', "C345")
        self.assert_json_equal('', 'article/@2/designation', "article N°3")
        self.assert_json_equal('', 'article/@2/price', 45.74)
        self.assert_json_equal('', 'article/@2/unit', '')
        self.assert_json_equal('', 'article/@2/stockable', 0)

        self.assert_json_equal('', 'article/@3/reference', "D456")
        self.assert_json_equal('', 'article/@3/designation', "article N°4")
        self.assert_json_equal('', 'article/@3/price', 56.89)
        self.assert_json_equal('', 'article/@3/unit', 'm')
        self.assert_json_equal('', 'article/@3/stockable', 2)

        self.factory.xfer = ArticleShow()
        self.calljson('/diacamma.invoice/articleShow', {'article': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleShow')
        self.assert_count_equal('', 17)
        self.assert_json_equal('LABELFORM', 'reference', "A123")
        self.assert_json_equal('LABELFORM', 'custom_1', 4)
        self.assert_json_equal('', '#custom_1/formatnum', {'0': '---', '1': 'noir', '2': 'blanc', '3': 'rouge', '4': 'bleu', '5': 'jaune'})
        self.assert_json_equal('LABELFORM', 'custom_2', 15)
        self.assert_json_equal('', '#custom_2/formatnum', "N0")

    def test_article_same_name(self):
        default_categories()
        default_articles()

        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('article', 4)
        self.assert_json_equal('', 'article/@0/reference', "ABC1")
        self.assert_json_equal('', 'article/@0/id', 1)
        self.assert_json_equal('', 'article/@1/reference', "ABC2")
        self.assert_json_equal('', 'article/@2/reference', "ABC3")
        self.assert_json_equal('', 'article/@3/reference', "ABC4")

        self.factory.xfer = ArticleAddModify()
        self.calljson('/diacamma.invoice/articleAddModify', {'article': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleAddModify')
        self.assert_count_equal('', 13)
        self.assert_json_equal('EDIT', 'reference', 'ABC1')

        self.factory.xfer = ArticleAddModify()
        self.calljson('/diacamma.invoice/articleAddModify',
                      {'article': '1', 'reference': 'ABC1', 'designation': 'Article 01', 'price': '12.34', 'accountposting': 1, 'stockable': '1', 'qtyDecimal': '3', 'SAVE': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'articleAddModify')

        self.factory.xfer = ArticleAddModify()
        self.calljson('/diacamma.invoice/articleAddModify',
                      {'article': '1', 'reference': 'ABC2', 'designation': 'Article 02', 'price': '12.34', 'accountposting': 1, 'stockable': '1', 'qtyDecimal': '3', 'SAVE': 'YES'}, False)
        self.assert_observer('core.exception', 'diacamma.invoice', 'articleAddModify')

        self.factory.xfer = ArticleAddModify()
        self.calljson('/diacamma.invoice/articleAddModify',
                      {'reference': 'ABC1', 'designation': 'Article 01', 'price': '12.34', 'accountposting': 1, 'stockable': '1', 'qtyDecimal': '3', 'SAVE': 'YES'}, False)
        self.assert_observer('core.exception', 'diacamma.invoice', 'articleAddModify')

    def test_article_kit(self):
        default_categories()
        default_articles(with_storage=True)

        self.factory.xfer = ArticleAddModify()
        self.calljson('/diacamma.invoice/articleAddModify',
                      {'reference': 'KIT01', 'designation': 'My beautiful kit', 'price': '68.74', 'accountposting': 4, 'stockable': 4, 'qtyDecimal': 0, 'SAVE': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'articleAddModify')

        self.factory.xfer = ArticleShow()
        self.calljson('/diacamma.invoice/articleShow', {'article': 6}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleShow')
        self.assert_count_equal('', 15)
        self.assert_json_equal('LABELFORM', 'reference', "KIT01")
        self.assert_json_equal('LABELFORM', 'designation', "My beautiful kit")
        self.assert_json_equal('LABELFORM', 'price', 68.74)
        self.assert_json_equal('LABELFORM', 'stockable', 4)
        self.assert_json_equal('LABELFORM', 'categories', [])
        self.assert_json_equal('LABELFORM', 'qtyDecimal', '0')
        self.assert_count_equal('storage', 1)
        self.assert_json_equal('', 'storage/@0/area', {"value": "Total", "format": "{[b]}{0}{[/b]}"})
        self.assert_json_equal('', 'storage/@0/qty', {"value": "0", "format": "{[b]}{0}{[/b]}"})
        self.assert_json_equal('', 'storage/@0/amount', {"value": 0, "format": "{[b]}{0}{[/b]}"})
        self.assert_json_equal('', 'storage/@0/mean', '')
        self.assert_json_equal('', 'storage/@0/available', {"value": '0', "format": "{[b]}{0}{[/b]}"})
        self.assert_grid_equal('kit_article', {'link_article': "article associé", "link_article.designation": "désignation", "link_article.available_total": "disponible", 'quantity_txt': "quantité dans la recette"}, 0)

        self.factory.xfer = RecipeKitArticleAddModify()
        self.calljson('/diacamma.invoice/recipeKitArticleAddModify', {'article': 6}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'recipeKitArticleAddModify')
        self.assert_count_equal('', 7)
        self.assert_json_equal('LABELFORM', 'article', 6)
        self.assert_select_equal('link_article', {1: 'ABC1 | Article 01 (0.0kg)', 2: 'ABC2 | Article 02 (0.0l)'})
        self.assert_json_equal('FLOAT', 'quantity', 1.0)

        self.factory.xfer = RecipeKitArticleAddModify()
        self.calljson('/diacamma.invoice/recipeKitArticleAddModify',
                      {'article': 6, 'quantity': 2, 'link_article': 1, 'SAVE': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'recipeKitArticleAddModify')

        self.factory.xfer = RecipeKitArticleAddModify()
        self.calljson('/diacamma.invoice/recipeKitArticleAddModify',
                      {'article': 6, 'quantity': 3, 'link_article': 2, 'SAVE': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'recipeKitArticleAddModify')

        self.factory.xfer = ArticleShow()
        self.calljson('/diacamma.invoice/articleShow', {'article': 6}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleShow')
        self.assert_count_equal('', 15)
        self.assert_count_equal('kit_article', 2)
        self.assert_json_equal('', 'kit_article/@0/id', 2)
        self.assert_json_equal('', 'kit_article/@0/link_article', 'ABC2')
        self.assert_json_equal('', 'kit_article/@0/quantity_txt', '3,0')
        self.assert_json_equal('', 'kit_article/@1/id', 1)
        self.assert_json_equal('', 'kit_article/@1/link_article', 'ABC1')
        self.assert_json_equal('', 'kit_article/@1/quantity_txt', '2,000')
        self.assert_count_equal('storage', 1)

        self.factory.xfer = RecipeKitArticleDel()
        self.calljson('/diacamma.invoice/recipeKitArticleDel',
                      {'kit_article': 1, 'CONFIRME': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'recipeKitArticleDel')

        self.factory.xfer = RecipeKitArticleAddModify()
        self.calljson('/diacamma.invoice/recipeKitArticleAddModify',
                      {'kit_article': 2, 'article': 6, 'quantity': 4, 'link_article': 1, 'SAVE': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'recipeKitArticleAddModify')

        self.factory.xfer = ArticleShow()
        self.calljson('/diacamma.invoice/articleShow', {'article': 6}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleShow')
        self.assert_count_equal('', 15)
        self.assert_count_equal('kit_article', 1)
        self.assert_json_equal('', 'kit_article/@0/id', 2)
        self.assert_json_equal('', 'kit_article/@0/link_article', 'ABC1')
        self.assert_json_equal('', 'kit_article/@0/quantity_txt', '4,000')
        self.assert_count_equal('storage', 1)

    def test_article_multiprice(self):
        default_categories()
        default_articles(with_storage=True, vat_mode=0)
        default_customize()
        default_multiprice()
        initial_thirds_fr()

        self.factory.xfer = ArticleAddModify()
        self.calljson('/diacamma.invoice/articleAddModify', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleAddModify')
        self.assert_count_equal('', 17)
        self.assert_json_equal('EDIT', 'reference', '')
        self.assert_json_equal('MEMO', 'designation', '')
        self.assert_json_equal('FLOAT', 'price', 0.0)
        self.assert_json_equal('', '#price/description', 'prix')
        self.assert_json_equal('FLOAT', 'price_1', 0.0)
        self.assert_json_equal('', '#price_1/description', 'price A')
        self.assert_json_equal('FLOAT', 'price_2', 0.0)
        self.assert_json_equal('', '#price_2/description', 'price B')
        self.assert_json_equal('SELECT', 'accountposting', 0)
        self.assert_json_equal('SELECT', 'stockable', '0')
        self.assert_json_equal('FLOAT', 'qtyDecimal', '0')

        self.factory.xfer = ArticleAddModify()
        self.calljson('/diacamma.invoice/articleAddModify',
                      {'reference': 'ABC001', 'designation': 'My beautiful article', 'price': '43.72', 'price_1': '39.99', 'price_2': '34.49', 'accountposting': 4, 'stockable': '1', 'qtyDecimal': '1', 'SAVE': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'articleAddModify')

        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('article', 5)
        self.assert_json_equal('', 'article/@0/reference', "ABC001")
        self.assert_json_equal('', 'article/@0/designation', "My beautiful article")
        self.assert_json_equal('', 'article/@0/price', 43.72)
        self.assert_json_equal('', 'article/@0/unit', '')
        self.assert_json_equal('', 'article/@0/stockable', 1)

        self.factory.xfer = ArticleShow()
        self.calljson('/diacamma.invoice/articleShow', {'article': '6'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleShow')
        self.assert_count_equal('', 22)
        self.assert_json_equal('', 'reference', 'ABC001')
        self.assert_json_equal('', 'designation', 'My beautiful article')
        self.assert_json_equal('', 'price', 43.72)
        self.assert_json_equal('', '#price/description', 'prix')
        self.assert_json_equal('', 'price_1', 39.99)
        self.assert_json_equal('', '#price_1/description', 'price A')
        self.assert_json_equal('', 'price_2', 34.49)
        self.assert_json_equal('', '#price_2/description', 'price B')
        self.assert_json_equal('', 'accountposting', "code4")
        self.assert_json_equal('', 'stockable', '1')
        self.assert_json_equal('', 'qtyDecimal', '1')

    def get_print_model(self):
        print_model = PrintModel.objects.create(name="Listing", kind="0", modelname="invoice.Article")
        print_model.value = """210
297
10//reference//#reference
40//designation//#designation
10//price//#current_price_txt
15//categories//#categories
10//quantities//#stockage_total
"""
        print_model.save()
        return print_model

    def test_article_print_multiprice_nothird(self):
        default_categories()
        default_articles(with_storage=True, vat_mode=0)
        default_customize()
        default_multiprice()
        initial_thirds_fr()
        print_model = self.get_print_model()

        self.factory.xfer = ArticlePrint()
        self.factory.user = LucteriosUser.objects.filter(username='admin').first()
        self.calljson('/diacamma.invoice/articlePrint', {'MODEL': print_model.id, 'PRINT_MODE': 4}, False)
        self.assert_observer('core.print', 'diacamma.invoice', 'articlePrint')
        csv_value = b64decode(str(self.response_json['print']['content'])).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 17, str(content_csv))
        self.assertEqual(content_csv[7], '"ABC1";"Article 01";"12,34 €";"cat 1";"0,000";')
        self.assertEqual(content_csv[8], '"ABC2";"Article 02";"56,78 €";"cat 2";"0,0";')
        self.assertEqual(content_csv[9], '"ABC3";"Article 03";"324,97 €";"cat 2,cat 3";"---";')
        self.assertEqual(content_csv[10], '"ABC4";"Article 04";"1,31 €";"cat 3";"0";')

    def test_article_print_multiprice_third(self):
        default_categories()
        default_articles(with_storage=True, vat_mode=0)
        default_customize()
        default_multiprice()
        initial_thirds_fr()
        print_model = self.get_print_model()

        contact = Individual.objects.filter(third__id=5).first()
        contact.user = LucteriosUser.objects.create(username=contact.create_username(), is_superuser=True)
        contact.save()

        self.factory.xfer = ArticlePrint()
        self.factory.user = contact.user
        self.calljson('/diacamma.invoice/articlePrint', {'MODEL': print_model.id, 'PRINT_MODE': 4}, False)
        self.assert_observer('core.print', 'diacamma.invoice', 'articlePrint')
        csv_value = b64decode(str(self.response_json['print']['content'])).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 17, str(content_csv))
        self.assertEqual(content_csv[7], '"ABC1";"Article 01";"11,11 €";"cat 1";"0,000";')
        self.assertEqual(content_csv[8], '"ABC2";"Article 02";"51,10 €";"cat 2";"0,0";')
        self.assertEqual(content_csv[9], '"ABC3";"Article 03";"292,47 €";"cat 2,cat 3";"---";')
        self.assertEqual(content_csv[10], '"ABC4";"Article 04";"1,18 €";"cat 3";"0";')
