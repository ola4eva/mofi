# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright 2019 EquickERP
#
##############################################################################
{
    'name': "Dynamic Purchase Approval",
    'category': 'Purchase',
    'version': '15.1.0',
    'author': 'Olalekan Babawale',
    'description': """
        This module allows you to approve purchase order users or group wise.
    """,
    'summary': """
        Dynamic Purchase Approval
    """,
    'depends': [
        'base',
        'purchase'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/config_po_approval.xml',
        'views/purchase_order_view.xml'
    ],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
