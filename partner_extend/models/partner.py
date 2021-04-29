# -*- coding: utf-8 -*-


from odoo import api, fields, models

class ResPartner(models.Model):
	_inherit = 'res.partner'

	sous_traitant = fields.Boolean('Sous traitant')

	property_account_rg_id = fields.Many2one('account.account', company_dependent = True,
													 string = "Compte de retenue de garantie",
													 domain = "[('internal_type', '=', 'receivable'), ('deprecated', '=', False)]",
													 )
	property_account_fin_rg_id = fields.Many2one('account.account', company_dependent = True,
													 string = "Compte de RG fin de travaux",
													 domain = "[('internal_type', '=', 'receivable'), ('deprecated', '=', False)]",
													 )
	old_account = fields.Char('Ancien compte')

class AccountPaymentTerm(models.Model):
	_inherit = 'account.payment.term'

	code = fields.Char('Code')