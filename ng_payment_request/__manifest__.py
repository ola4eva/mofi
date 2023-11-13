{
    'name': 'Payment Request',
    'version': '11.0',
    'author': 'Mattobell',
    'website': 'http://www.mattobell.com/',
    'description': "Payment Request",
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/request_sequence.xml',
        'views/payment_requisition_view.xml',
        'views/company_view.xml',
        'views/payment_request_report.xml',
        'views/request_report_view.xml',
    ],
    'depends': [
        'account_accountant',
        'hr'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
