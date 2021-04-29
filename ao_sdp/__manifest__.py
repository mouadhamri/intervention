# -*- coding: utf-8 -*-
{
    "name": "AO SDP",
    "version": "1.0",
    "category": "PMO",
    "description": """ 
    AO / SDP.
    """,
    'author': 'SYENTYS',
    'website': 'http://www.syentys.com',
    "depends": ['base','ao','analytic','project_wbs'],
    "data": [
        "views/wbs.xml",
        "views/ao_menu.xml",
        "security/sdp_security.xml",
        "security/ir.model.access.csv",
    ],
    'demo': [],
    "active": True,
    "installable": False,
    'applcation': False,
    'auto_install': False,
}