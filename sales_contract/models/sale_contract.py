# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class SaleContract(models.Model):
    _name = 'sale.contract'
    _order = 'date_end desc'

    name = fields.Char('Numéro', default='/', required=True)
    customer_id = fields.Many2one('res.partner', 'Client', required=True)
    date_start = fields.Date('Date début')
    date_end = fields.Date('Date fin')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company.id)
    pricelist_id = fields.Many2one('product.pricelist', 'Liste de prix')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company.id)
    commentaire = fields.Text('Commentaire')
    contract_actif = fields.Boolean(compute='compute_contact_actif')
    line_ids = fields.One2many('sale.contract.line', 'contract_id', 'Détail', copy=True)
    state = fields.Selection([('draft', 'Nouveau'), ('confirm', 'Validé')], default='draft')

    def set_contract_to_draft(self):
        for rec in self:
            self.pricelist_id.active = False
            self.pricelist_id = False
            self.state = 'draft'

    @api.model
    def create(self, vals):
        if not vals.get('name', False) or vals['name'] == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('sale.contract')
        return super(SaleContract, self).create(vals)

    def compute_contact_actif(self):
        for rec in self:
            rec.contract_actif = rec.date_start and rec.date_start <=fields.Date.context_today(self) and\
                                 (not rec.date_end or rec.date_end > fields.Date.context_today(self))

    def Validate_contract(self):
        for rec in self:
            if not rec.date_end or rec.date_end >= fields.Date.context_today(self):
                new_pricelist = self.env['product.pricelist'].create(
                    {'name': 'Liste de prix du ' + str(rec.name) + 'client ' + str(rec.customer_id.name)})

                for line in rec.line_ids:
                    if line.type == 'price':
                        self.env['product.pricelist.item'].create({
                            'applied_on': '1_product',
                            'product_tmpl_id': line.product_id.id,
                            'date_start': rec.date_start or False,
                            'date_end': rec.date_end or False,
                            'compute_price': 'fixed',
                            'fixed_price': line.price,
                            'pricelist_id': new_pricelist.id

                        })
                    elif line.type == "discount":
                        self.env['product.pricelist.item'].create({
                            'applied_on': '1_product',
                            'product_tmpl_id': line.product_id.id,

                            'date_start': rec.date_start or False,
                            'date_end': rec.date_end or False,
                            'compute_price': 'percentage',
                            'percent_price': line.discount,
                            'pricelist_id': new_pricelist.id

                        })

                rec.pricelist_id = new_pricelist.id
                rec.customer_id.property_product_pricelist = new_pricelist.id
                rec.state = 'confirm'


class SaleContractLine(models.Model):
    _name = 'sale.contract.line'

    product_id = fields.Many2one('product.template', "Article", required=True)
    type = fields.Selection([('price', 'Prix'), ('discount', 'Remise')], default='discount')
    price = fields.Float('Prix')
    discount = fields.Float('Remise')
    contract_id = fields.Many2one('sale.contract', 'Contrat', ondelete='cascade')
    product_uom_id = fields.Many2one('uom.uom', 'Udm')

    @api.onchange('product_id')
    def onchnage_product(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id
