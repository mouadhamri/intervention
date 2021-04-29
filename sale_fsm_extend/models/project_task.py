# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError

from datetime import timedelta, datetime

class ProjectTask(models.Model):
	_inherit = 'project.task'

	@api.model
	def _read_group_user_ids(self, users, domain, order):
		if self.env.context.get('fsm_mode'):
			domain_task = [
							  ('create_date', '>', datetime.now() - timedelta(days = 30)),
							  ('is_fsm', '=', True),
							  ('user_id', '!=', False)] + domain
			recently_created_tasks = self.env['project.task'].search(domain_task)
			# search_domain = ['|', '|', ('id', 'in', users.ids),
			#                  ('groups_id', 'in', self.env.ref('industry_fsm.group_fsm_user').id),
			#                  ('id', 'in', recently_created_tasks.mapped('user_id.id'))]
			search_domain = [
				('groups_id', 'in', self.env.ref('industry_fsm.group_fsm_user').id),
				('id', 'in', recently_created_tasks.mapped('user_id.id'))]
			print('search_domain', search_domain)
			print('usersusers', users)
			print('recently_created_tasks', recently_created_tasks)
			return users.search(search_domain, order = order)
		return users

	fsm_sale_id = fields.Many2one('sale.order', 'Bon de commande', ondelete='cascade')
	fsm_state = fields.Selection(
		[('draft', 'Nouveau'), ('attente', 'En attente de validation'), ('done', 'Fait'), ('confirm', 'Validé')],
		string = "Etat",
		default = 'draft')
	fsm_status_id = fields.Many2one('project.task.status', 'ETAT INTER')
	bailleur_id = fields.Many2one('res.partner', 'Bailleur')
	en_attente = fields.Boolean('En attente', compute = "compute_en_attente", store = True)
	fsm_sav = fields.Boolean('SAV', default = False)
	fsm_sav_ids = fields.One2many('project.task', 'fsm_id', 'SAV', domain = [('fsm_sav', '=', True)])
	fsm_id = fields.Many2one('project.task', "Intervention d'origine")
	fsm_sav_count = fields.Integer('SAV', compute = "compute_fsm_sav_count", store = True)
	is_fsm = fields.Boolean(related = '', search = '', default = False)
	nom_client_final = fields.Char('Nom/prénom', related = 'fsm_sale_id.nom_client_final', store = True)
	appart_client_final = fields.Char('N° appartement', related = 'fsm_sale_id.appart_client_final', store = True)
	ville_client_final = fields.Char('Ville', related = 'fsm_sale_id.ville_client_final', store = True)
	tel_client_final = fields.Char('Tél', related = 'fsm_sale_id.tel_client_final', store = True)
	code_postal_final = fields.Char('Code postal', related = 'fsm_sale_id.code_postal', store = True)
	partner_address_1 = fields.Char("Ligne d'adresse 1", related = 'fsm_sale_id.partner_address_1', store = True)
	has_edit_acces = fields.Boolean(compute = 'compute_has_edit_acces')
	planned_date_begin = fields.Datetime("Start date", tracking = True)
	planned_date_end = fields.Datetime("End date", tracking = True)
	conducteur_travaux_id = fields.Many2one('res.users', related = 'project_id.conducteur_travaux_id', store = True)
	client_order_ref = fields.Char(string = 'N° BC client', related = 'fsm_sale_id.client_order_ref')
	intervenant_ids = fields.Many2many('res.users', string = 'INTERVENANTS SUPPL', relation = 'inetrvenant_task_rel')
	last_state = fields.Boolean(string = 'Etat finale', related = 'fsm_status_id.last_state',
									  store = True)
	fournitures_info_divers = fields.Html(string='FOURNITURES/Info divers')

	def fsm_special_validate(self):
		self.write({'fsm_state': 'confirm'})

	#
	@api.onchange('fsm_sale_id')
	def onchange_fsm_sale_id(self):
		if self.fsm_sale_id:
			self.partner_id = self.fsm_sale_id.partner_id.id
			self.project_id = self.fsm_sale_id.chantier_id and self.fsm_sale_id.chantier_id.id or False
			self.bailleur_id = self.fsm_sale_id.bailleur_id and self.fsm_sale_id.bailleur_id.id or False

	@api.onchange('project_id')
	def onchange_project(self):
		if self.project_id and self.project_id.bailleur_id:
			self.bailleur_id = self.project_id.bailleur_id.id
		if self.project_id and self.project_id.analytic_account_id:
			self.analytic_account_id = self.project_id.analytic_account_id.id
		if self.project_id and self.fsm_sale_id:
			if self.project_id.partner_id and self.project_id.partner_id != self.fsm_sale_id.partner_id:
				self.fsm_sale_id = False

	@api.depends('user_id')
	def compute_has_edit_acces(self):
		for rec in self:
			if self.env.user.user_has_groups('industry_fsm.group_fsm_manager, project.group_project_manager'):
				rec.has_edit_acces = True
			else:
				rec.has_edit_acces = False

	@api.model
	def create(self, vals):
		res = super(ProjectTask, self).create(vals)

		if res.fsm_sale_id and vals.get('fsm_status_id', False):
			statut = vals['fsm_status_id']
			res.fsm_sale_id.fsm_status_id = statut
		return res

	def write(self, values):
		result = super(ProjectTask, self).write(values)
		for rec in self:
			if values.get('fsm_status_id', False):
				if rec.fsm_sale_id:
					rec.fsm_sale_id.fsm_status_id = rec.fsm_status_id.id
		return result

	def _sms_get_number_fields(self):
		""" This method returns the fields to use to find the number to use to
		send an SMS on a record. """
		return ['mobile', 'phone']

	def fsm_sav_action(self):
		self.ensure_one()
		context = {'fsm_mode': True,
				   'fsm_sav': True,
				   'show_address': True,
				   'search_default_my_tasks': True,
				   'search_default_planned_future': True,
				   'search_default_planned_today': True,
				   'fsm_task_kanban_whole_date': False,
				   'default_is_fsm': True,
				   'default_fsm_sav': True,
				   'default_fsm_id': self.id,
				   'default_partner_id': self.partner_id.id,
				   'default_partner_email': self.partner_id.email,
				   'default_bailleur_id': self.bailleur_id and self.bailleur_id.id or False,
				   'default_project_id': self.project_id and self.project_id.id
				   }

		return {'type': 'ir.actions.act_window',
				'name': "Interventions",
				'res_model': 'project.task',
				'view_mode': 'tree,form,map,kanban,gantt,calendar,activity',
				'domain': [('fsm_id', '=', self.id), ('fsm_sav', '=', True)],
				'context': context,
				'target': 'current',
				}

	@api.depends('fsm_sav_ids')
	def compute_fsm_sav_count(self):
		for rec in self:
			if rec.fsm_sav_ids:
				rec.fsm_sav_count = len(rec.fsm_sav_ids)
			else:
				rec.fsm_sav_count = 0

	@api.depends('planned_date_begin')
	def compute_en_attente(self):
		for rec in self:
			if not rec.planned_date_begin:
				rec.en_attente = True
			else:
				rec.en_attente = False

	def fsm_confirm_action_done(self):
		if any(not l.last_state for l in self):
			raise UserError("L'état des interventions n'est pas finale!")
		self.write({'fsm_state': 'done', 'fsm_done': True})

	def fsm_mettre_en_attente(self):
		self.write({'fsm_state': 'attente'})

	def fsm_mettre_a_nouveau_action(self):
		self.write({'fsm_state': 'draft',
					'fsm_done': False})

	def fsm_report(self):
		for rec in self:
			rec.planned_date_begin = False
			rec.planned_date_end = False

	def fsm_confirm_action(self):
		if any(not l.last_state for l in self):
			raise UserError("L'état des interventions n'est pas finale!")
		self.write({'fsm_state': 'confirm'})


class ProjetTaskStatus(models.Model):
	_name = 'project.task.status'

	code = fields.Char('Etat')
	name = fields.Char(string = 'Descriptif', required = True)
	last_state = fields.Boolean(string = 'Etat finale')


class Project(models.Model):
	_inherit = 'project.project'

	conducteur_travaux_id = fields.Many2one('res.users', domain = "[('charge_affaire', '=', True)]")
