

from odoo import api, fields, models

class ProjectFinancierReport(models.AbstractModel):
	_name = "report.project_report.financier_report"

	@api.model
	def _get_report_values(self, docids, data = None):
		docs = self.env['project.project'].browse(docids).sudo()

		facture_fournisseur = {}
		facture_client = {}
		timesheet_dict = {}
		expense_dict = {}
		divers_dict = {}
		total_cost_proj = {}
		total_sale_proj = {}
		prix_revient_marge_proj = {}
		revenu_prevu_amount_proj = {}
		percent_invoice_proj = {}
		coef_vente_proj = {}
		for project in docs:
			total_cost = 0.0
			total_sale = 0.0
			######Facture fournisseur
			facture_fournisseur[project.id] = {'detail':[], 'total':0.0}
			facture_fournisseurs = self.env['account.move.line'].search([('analytic_account_id', '=', project.analytic_account_id.id),
																		('move_id.move_type', 'in', ('in_invoice', 'in_refund')),
																		 ('parent_state', 'not in', ('draft', 'cancel'))])

			if facture_fournisseurs:
				facture_fournisseur[project.id]['total'] = sum(line.debit or (-1)* line.credit for line in facture_fournisseurs)
				total_cost += facture_fournisseur[project.id]['total']
				for line in facture_fournisseurs.sorted(key=lambda r:r.date):
					facture_fournisseur[project.id]['detail'].append({
						'invoice_id': line.move_id,'date': line.date,
														 'partner':line.move_id.partner_id,
														 'amount': line.debit or (-1)* line.credit,
														 'text': "Fac.["+line.move_id.name+"] du "+str(line.date)+" - "+line.move_id.partner_id.name

														 })

			######Facture client

			facture_client[project.id] = {'detail':[], 'total':0.0}
			facture_clients = self.env['account.move.line'].search([('analytic_account_id', '=', project.analytic_account_id.id),
																		('move_id.move_type', 'in', ('out_invoice', 'out_refund')),
																	('parent_state', 'not in', ('draft', 'cancel'))])

			if facture_clients:
				facture_client[project.id]['total'] = sum(line.credit or (-1)* line.debit for line in facture_clients)
				total_sale += facture_client[project.id]['total']
				for line in facture_clients.sorted(key=lambda r:r.date):
					facture_client[project.id]['detail'].append({
						'invoice_id': line.move_id,'date': line.date,
														 'partner':line.move_id.partner_id,
														 'amount': line.credit or (-1)* line.debit,
														 'text': "Fac.["+line.move_id.name+"] du "+str(line.date)+" - "+line.move_id.partner_id.name

														 })
			######Main d'oeuvre
			timesheet_dict[project.id]={}
			timesheet_ids = self.env['account.analytic.line'].search([('project_id', '=', project.id), ('user_id', '!=', False)])
			if timesheet_ids:
				timesheet_dict[project.id]['total_h'] = sum(l.unit_amount for l in timesheet_ids)
				timesheet_dict[project.id]['total_amount'] = sum(l.unit_amount * (l.employee_id and l.employee_id.timesheet_cost or 1) for l in timesheet_ids)
				total_cost += timesheet_dict[project.id]['total_amount']
			######Dépense
			expense_dict[project.id]={'detail':{}, 'total':0.0}
			expense_ids = self.env['hr.expense'].search([('analytic_account_id', '=', project.analytic_account_id.id)])
			if expense_ids:
				expense_dict[project.id]['total'] = sum(l.untaxed_amount for l in expense_ids)
				total_cost += expense_dict[project.id]['total']
				for l in expense_ids:
					if expense_dict[project.id]['detail'].get(l.product_id.name, False):
						expense_dict[project.id]['detail'][l.product_id.name]+= l.untaxed_amount
					else:
						expense_dict[project.id]['detail'][l.product_id.name] = l.untaxed_amount
			######frais divers
			divers_dict[project.id]={'detail':{}, 'total':0.0}
			divers_ids = self.env['account.analytic.line'].search([('account_id', '=', project.analytic_account_id.id),
																   ('account_journal_id.type', '=', 'general')])
			print('divers_idsdivers_ids', divers_ids)
			if divers_ids:
				divers_dict[project.id]['total'] = sum((-1) * l.amount for l in divers_ids)
				total_cost += divers_dict[project.id]['total']
				for l in divers_ids:
					if l.gen_account_id:
						if divers_dict[project.id]['detail'].get(l.gen_account_id.code, False):
							divers_dict[project.id]['detail'][l.gen_account_id.code]+= (-1) * l.amount
						else:
							divers_dict[project.id]['detail'][l.gen_account_id.code] = (-1) * l.amount
					else:
						if divers_dict[project.id]['detail'].get(l.name, False):
							divers_dict[project.id]['detail'][l.name]+= (-1) * l.amount
						else:
							divers_dict[project.id]['detail'][l.name] = (-1) * l.amount
			print('divers_dictdivers_dict', divers_dict)

			total_cost_proj[project.id] = total_cost
			total_sale_proj[project.id] = total_sale
			prix_revient_marge_proj[project.id] = total_cost * (1 + project.marge_souhaite/100)
			forecast_ids = self.env['account.analytic.line'].search([('account_id', '=', project.analytic_account_id.id),
																	 ('type', '=', 'f'),
																	 ('amount', '>', 0)])
			revenu_prevu_amount = sum(l.amount for l in forecast_ids)
			revenu_prevu_amount_proj[project.id] = revenu_prevu_amount
			percent_invoice_proj[project.id] = revenu_prevu_amount and (total_sale/revenu_prevu_amount)*100 or 0
			coef_vente_proj[project.id] = total_cost and (total_sale/total_cost) or 0




		return {
			'doc_ids': docids,
			'doc_model': 'project.project',
			'docs': docs,
			'facture_fournisseur':facture_fournisseur,
			'facture_client':facture_client,
			'timesheet_dict':timesheet_dict,
			'expense_dict': expense_dict,
			'divers_dict': divers_dict,
			'total_cost':total_cost_proj,
			'total_sale':total_sale_proj,
			'prix_revient_marge':prix_revient_marge_proj,
			'revenu_prevu_amount':revenu_prevu_amount_proj,
			'percent_invoice':percent_invoice_proj,
			'coef_vente':coef_vente_proj,

		}
