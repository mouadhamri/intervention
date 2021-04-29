# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductTemplate(models.Model):
	_inherit = 'product.template'

	generic = fields.Boolean('Article générique')
	contract_line_ids = fields.One2many('sale.contract.line', 'product_id')


class SaleOrder(models.Model):
	_inherit = 'sale.order'

	active_contract = fields.Many2one('sale.contract','Contrat actif', compute='compute_actif_contract', store=True)

	@api.depends('partner_id')
	def compute_actif_contract(self):
		for rec in self:
			active_contract =False
			if rec.partner_id and rec.partner_id.contract_ids:
				active_contract = rec.partner_id.contract_ids.filtered(lambda r: r.date_start and r.date_start <=fields.Date.context_today(self) and
																					 (not r.date_end or r.date_end > fields.Date.context_today(self))
																	   and r.state == 'confirm')
				if active_contract:
					active_contract = active_contract[0].id
			rec.active_contract = active_contract


class SaleOrderLine(models.Model):
	_inherit = 'sale.order.line'

	active_contract = fields.Many2one(related='order_id.active_contract' , store=True)


