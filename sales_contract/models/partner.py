# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    contract_ids = fields.One2many('sale.contract', 'customer_id', 'Contrats' )
    contract_count = fields.Integer(compute='compute_contract_count')


    def compute_contract_count(self):
        for rec in self:
            rec.contract_count = len(rec.contract_ids)


    def view_partner_contracts(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Contrats',
            'res_model': 'sale.contract',
            'view_mode': 'tree,form',
            'domain': [('customer_id', '=', self.id)],
            'context': dict(self._context, create=False, default_company_id=self.env.company.id
                          ),
        }


