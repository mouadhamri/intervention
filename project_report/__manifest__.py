# -*- coding: utf-8 -*-
{
    'name': "Rapport Analyse financière",
    'description': """
        Rapport Analyse financière

    """,
    'author': 'Andema',
    'website': 'http://www.andemaconsulting.com',
    'category': 'Services/Project',
    'version': '0.1',
    'depends': ['base', "project","project_extend"],
    'data': [
        'views/project_views.xml',
        'report/project_report.xml',
        'report/project_report_template.xml',
    ],
    'installable': True,
    'application': False,
    'active': True
}