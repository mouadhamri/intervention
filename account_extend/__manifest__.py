# -*- coding: utf-8 -*-
{
    'name': "account_extend",

    'summary': """
        Accounting Extension""",

    'author': "ANDEMA",
    'website': "http://www.andemaconsulting.com",
    'version': '0.5',
    'depends': ["base","account","account_accountant", "sale", "sale_fsm_extend", 'crm','analytic',
                'sales_team', 'account_reports', 'partner_extend','sale_templates'],
    'data': [
        'security/security.xml',

        'security/ir.model.access.csv',
        'data/followup_template.xml',
        'views/accounting_views.xml',
        'views/sales_views.xml',
        'views/partner_views.xml',
        'views/account_move_views.xml',
        'report/invoice_report_template.xml',
        'report/report_config.xml',
        'report/gecop_invoice_report.xml',
        'report/gecop_invoice_valophis_report.xml',
        'report/gecop_invoice_rivp_report.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
