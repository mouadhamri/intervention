# -*- coding: utf-8 -*-
{
    "name": "Dépannage",
    "version": "1.0",
    "category": "Operations/Field Service",
    "description": """ 
    Field service extend
    """,
    'author': 'SYENTYS',
    'website': 'http://www.syentys.com',
  #  "depends": ['base','industry_fsm','sale', 'project_wbs', 'ao_sale'],
    "depends": ['base', 'sale', 'industry_fsm', 'timesheet_grid','web','web_enterprise', 'project_extend',
                'sale_timesheet', 'project_sale', 'account', 'base_automation', 'sale_templates', 'hr', 'l10n_fr'],

    "data": [
        'security/fsm_security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/fsm_task_views.xml',
        'views/sale_views.xml',
        'data/fsm_cron.xml',
        'views/template.xml',
        'views/hr_views.xml',
        'views/suivi_bc.xml',

    ],
    'css': ['static/src/css/page.css'],
    'demo': [],
    "active": True,
    "installable": True,
    'application': False,
    'auto_install': False,
}