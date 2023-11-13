# -*- coding: utf-8 -*-

{
    'name': 'Manual Currency Exchange Rate for Sales, Invoice, Bills and Purchase',
    'author': 'Edge Technologies',
    'version': '16.0.1.3',
    'live_test_url':'https://youtu.be/d890rvjWnjo',
    "license" : "OPL-1",
    "images":['static/description/main_screenshot.png'],
    'category': 'Accounting',
    'summary': 'Apply Manual exchange rate on invoice Manual currency exchange rate on sales Manual currency exchange rate on invoice exchange rate custom exchange rate payment manual currency exchange rate on purchase manual currency exchange rate currency custom rate',
    'description': "Currency Exchange Rate App",
    'depends': [
        'sale_management',
        'purchase',
        'stock',
        'account'
    ],
    'data': [
        'views/inherited_res_company.xml',
        'views/inherited_res_config_settings.xml',
        'views/inherited_sale_order_view.xml',
        'views/inherited_purchase_order_view.xml',
        'views/inherited_account_move_view.xml',
        'views/inherited_account_payment_view.xml',
    ],
    'qweb' : [],
    'demo': [],
    'css': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    "price": 15,
    "currency": 'EUR',
}
