# -*- coding: utf-8 -*-

from odoo import api, fields, models

class PartnerGeneralLedgerWizard(models.TransientModel):
    _name = "partner.general.ledger.wizard"


    date_from = fields.Date('Date début')
    date_to = fields.Date('Date fin')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, string="Société")

    def _prepare_report_general_ledger(self):
        self.ensure_one()
        data = {}
        return data

    def print_report (self):
        self.ensure_one()

        partners = self.env.context.get('active_ids', False)
        print('paaaaaaaa', partners)
        data = {
            'ids'  : partners,
            'model': 'res.partner',
            'date_from': self.date_from,
            'date_to'  : self.date_to,
            'company_id': self.company_id.id,



        }
        # report_name = "partner_general_ledger.report_partner_general_ledger"
        # return (
        #     self.env["ir.actions.report"]
        #     .search(
        #         [("report_name", "=", report_name), ("report_type", "=", "qweb-pdf")],
        #         limit=1,
        #     )
        action = self.env.ref('partner_general_ledger.action_report_partner_ledger').report_action(self, data=data)
        return action
        # )

