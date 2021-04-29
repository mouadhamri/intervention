# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    chantier_id = fields.Many2one('project.project', 'Chantier')


    def write(self, vals):
        if vals.get('chantier_id', False):
            chantier = self.env['project.project'].browse(vals['chantier_id'])
            if chantier and chantier.analytic_account_id:
                vals['analytic_account_id'] = chantier.analytic_account_id.id
        if vals.get('analytic_account_id', False) and not vals.get('chantier_id', False):
            analytic = self.env['account.analytic.account'].browse(vals['analytic_account_id'])
            chantier = self.env['project.project'].search([('analytic_account_id', '=', analytic.id)])
            if analytic and chantier:
                vals['chantier_id'] = chantier[0].id

        res = super(SaleOrder, self).write(vals)
        return res

    @api.model
    def create(self, vals):
        if vals.get('chantier_id', False):
            chantier = self.env['project.project'].browse(vals['chantier_id'])
            if chantier and chantier.analytic_account_id:
                vals['analytic_account_id'] = chantier.analytic_account_id.id
        if vals.get('analytic_account_id', False) and not vals.get('chantier_id', False):
            analytic = self.env['account.analytic.account'].browse(vals['analytic_account_id'])
            chantier = self.env['project.project'].search([('analytic_account_id', '=', analytic.id)])
            if analytic and chantier:
                vals['chantier_id'] = chantier[0].id
        res = super(SaleOrder, self).create(vals)
        return res



    @api.onchange('chantier_id')
    def onchange_chantier_id(self):
        if self.chantier_id:
            self.analytic_account_id = self.chantier_id.analytic_account_id and self.chantier_id.analytic_account_id.id
        if self.chantier_id and self.chantier_id.partner_id:
            self.partner_id = self.chantier_id.partner_id.id
            self.pricelist_id = self.chantier_id.partner_id.property_product_pricelist.id

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        res = super(SaleOrder, self).onchange_partner_id()
        if self.partner_id:
            chantier = self.env['project.project'].search([('partner_id', '=', self.partner_id.id),
                                                           '|',('date_end', '=', False),
                                                           ('date_end', '>=', fields.Date.context_today(self))])
            if chantier:
                self.chantier_id = chantier[0].id

        return res


