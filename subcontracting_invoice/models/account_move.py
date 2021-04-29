# -*- coding: utf-8 -*-


from odoo import api, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
	_inherit = 'account.move'


	sous_traitant_id = fields.Many2one('res.partner', domain="[('sous_traitant', '=', True)]")
	subcontracting_refund_id =  fields.Many2one('account.move', 'Avoir de sous-traitance')
	origin_invoice_ids = fields.One2many('account.move', 'subcontracting_refund_id', "Facture d'origine")
	subcontracting_refund = fields.Boolean()
	sous_traitant = fields.Boolean('partenaire sous-traitant', related = 'partner_id.sous_traitant', store = True)
	soustraitant = fields.Boolean('Facture de sous-traitant')

	def generate_subcontracting_refund(self):
		refund_journal = self.env['account.journal'].search([('type', '=', 'purchase')], limit=1)
		if not refund_journal:
			raise UserError("Aucun journal d'achat trouvé!")
		if any(l.subcontracting_refund_id for l in self):
			traite = self.filtered(lambda r:r.subcontracting_refund_id)
			raise UserError('Les facture %s sont déjà traitées'%(','.join(traite.mapped('name'))))

		partners = self.mapped('sous_traitant_id')
		refunds = []
		if partners:
			for partner in partners:
				invoices = self.filtered(lambda r: r.sous_traitant_id == partner)
				refund_id = self.env['account.move'].create({'partner_id': partner.id,
															 'move_type': 'in_refund',
															 'date': fields.Date.context_today(self),
															 'invoice_date': fields.Date.context_today(self),
															 'currency_id': self.env.company.currency_id.id,
															 'subcontracting_refund': True,
															 'invoice_origin': ','.join(str(invoices.mapped('name')))
															 })
				refunds.append(refund_id.id)
				lines = invoices.mapped('invoice_line_ids')
				if lines:
					refund_lines = []

					for line in lines:
						refund_lines.append((0,0, {'account_id': line.account_id.id,
												   'product_id': line.product_id and line.product_id.id or False,
												   'name': line.name,
												   'origin_invoice_line_id': line.id,
												   'quantity': line.quantity,
												   'price_unit': line.price_unit * (1 - (line.discount / 100.0)) * (1+ self.env.company.subcontracting_marge/100),
												   'product_uom_id': line.product_uom_id and line.product_uom_id.id or False,
												   'tax_ids': [(6,0, line.tax_ids.ids)],
												   'analytic_account_id': line.analytic_account_id and line.analytic_account_id.id,
												   'move_id': refund_id.id,
												   'exclude_from_invoice_tab': False
												   }))
					refund_id.write({'invoice_line_ids': refund_lines})


				if refund_id:
					invoices.write({'subcontracting_refund_id': refund_id.id})
		if refunds:
			action = self.env.ref(
				"account.action_move_in_refund_type"
			).read()[0]
			action["domain"] = [('id', 'in', refunds)]
			return action

class AccountMoveLine(models.Model):
	_inherit = 'account.move.line'

	origin_invoice_line_id = fields.Many2one('account.move.line')

class ResCompany(models.Model):
	_inherit = 'res.company'

	subcontracting_marge = fields.Float('Marge de soutraitance')


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    sous_traitant = fields.Boolean('Sous traitant', related='partner_id.sous_traitant', store=True)
