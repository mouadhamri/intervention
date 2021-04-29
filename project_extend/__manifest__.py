# -*- coding: utf-8 -*-
{
    "name": "Project extend",
    "version": "1.0",
    "category": "PMO",
    "description": """ 
   
    """,
    'author': 'Andema',
    'website': 'http://www.andemaconsulting.com',
    "depends": ['base','project', 'hr_timesheet', 'account_forecast', 'purchase', 'stock', 'hr_expense'],
    "data": [
        'security/project_security.xml',
        'security/ir.model.access.csv',
        "views/project_views.xml"
    ],
    'demo': [],
    "active": True,
    "installable": True,
    'application': False,
    'auto_install': False,
}