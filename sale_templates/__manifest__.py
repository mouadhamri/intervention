{
    'name': 'Sale templates',
    'version': '1.0.0',
    'category': 'Subscription',
    'author': 'Syentys',
    'license': 'OPL-1',
    'website': 'https://syentys.com',
    'depends': [
        'sale','web', 'project_sale'
    ],
    'data': [
        'security/signature_security.xml',
        'views/company_view.xml',
        'views/report_layout.xml',
        'views/sale_template.xml',
        'views/sale_template_second.xml',
        'views/report.xml',
        'views/sale_views.xml'


    ],
    'qweb': [],
    'installable': True,
    'application': False,

}
