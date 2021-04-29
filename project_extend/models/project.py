# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError


class Project(models.Model):
    _name = 'project.project'
    _inherit = ['project.project','mail.activity.mixin', 'portal.mixin', 'mail.alias.mixin', 'mail.thread', 'rating.parent.mixin']


    numero_marche = fields.Char(u'N° Marché')
    budget_ht = fields.Float('Budget HT')
    budget_ttc = fields.Float('Budget TTC')
    date_start = fields.Date('Date debut')
    date_end = fields.Date('Date fin')
    analytic_budget_count = fields.Float(u"Budget", compute = "get_analytic_budget_count")
    analytic_cost_count = fields.Float(u"Cost", compute = "get_analytic_cost_count")
    actual_analytic_line_ids = fields.One2many('account.analytic.line', 'chantier_id', domain=[('type', '=', 'a')])
    forecast_analytic_line_ids = fields.One2many('account.analytic.line', 'chantier_id', domain=[('type', '=', 'f')])
    conducteur_travaux_id = fields.Many2one('res.users', 'Conducteur des travaux')
    bailleur_id = fields.Many2one('res.partner', 'Bailleur')

    def get_analytic_budget_count(self):
        for record in self:
            forecast_analytic_lines = self.env['account.analytic.line'].search([("account_id", "=", self.analytic_account_id.id),
                                                                                ('type', '=', 'f')])
            record.analytic_budget_count = sum([f.amount for f in forecast_analytic_lines])

    def get_analytic_cost_count(self):
        for record in self:
            forecast_analytic_lines = self.env['account.analytic.line'].search([("account_id", "=", self.analytic_account_id.id),
                                                                                ('type', '=', 'a')])
            record.analytic_cost_count = sum([f.amount for f in forecast_analytic_lines])


    def get_budget_project_view(self):
        self.ensure_one()
        tree_view = self.env.ref('analytic.view_account_analytic_line_tree')
        form_view = self.env.ref('analytic.view_account_analytic_line_form')
        pivot_view = self.env.ref('analytic.view_account_analytic_line_pivot')
        budget_ids = []

        return {
            'name': 'Forecast',
            'type': 'ir.actions.act_window',
            'res_model': 'account.analytic.line',
            'view_type': 'form',
            'views': [(tree_view.id, 'tree'), (form_view.id, 'form'), (pivot_view.id, 'pivot')],
            'view_mode': 'tree,form',
            'domain': [("account_id", "=", self.analytic_account_id.id), ('type', '=', 'f')],
            'context': {'type': 'f', 'default_type': 'f',
                        'default_account_id': self.analytic_account_id.id,
                        'default_project_id': self.id
                        },
            'target': 'current',
        }


    def get_cost_project_view(self):
        tree_view = self.env.ref('analytic.view_account_analytic_line_tree')
        form_view = self.env.ref('analytic.view_account_analytic_line_form')
        pivot_view = self.env.ref('analytic.view_account_analytic_line_pivot')
        self.ensure_one()

        return {
            'name': 'Cost',
            'type': 'ir.actions.act_window',
            'res_model': 'account.analytic.line',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(tree_view.id, 'tree'), (form_view.id, 'form'), (pivot_view.id, 'pivot')],
            'domain': [("account_id", "=", self.analytic_account_id.id), ('type', '=', 'a')],
            'context': {'type': 'a', 'default_type': 'a',
                        'default_account_id': self.analytic_account_id.id,
                        'default_project_id': self.id},
            'target': 'current',
        }

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.user.has_group('project_extend.group_project_create_user'):
            raise UserError("Vous ne pouvez pas créer des projets. Consulter l'administrateur")
        res = super(Project, self).create(vals_list)
        return res

    def unlink(self):
        if not self.env.user.has_group('project_extend.group_project_create_user'):
            raise UserError("Vous ne pouvez pas supprimer des projets. Consulter l'administrateur")
        res = super(Project, self).unlink()
        return res



class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    chantier_id = fields.Many2one('project.project', compute='compute_chantier', store=True)

    @api.depends('account_id', 'account_id.project_ids')
    def compute_chantier(self):
        for rec in self:
            if rec.account_id and rec.account_id.project_ids:
                rec.chantier_id = rec.account_id.project_ids[0].id
            else:
                rec.chantier_id=False

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.user.has_group('project_extend.group_partner_create_user'):
            raise UserError("Vous ne pouvez pas créer des contacts. Consulter l'administrateur")
        res = super(ResPartner, self).create(vals_list)
        return res

    def unlink(self):
        if not self.env.user.has_group('project_extend.group_partner_create_user'):
            raise UserError("Vous ne pouvez pas supprimer des contacts. Consulter l'administrateur")
        res = super(ResPartner, self).unlink()
        return res

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.user.has_group('project_extend.group_product_create_user'):
            raise UserError("Vous ne pouvez pas créer des articles. Consulter l'administrateur")
        res = super(ProductTemplate, self).create(vals_list)
        return res


    def unlink(self):
        if not self.env.user.has_group('project_extend.group_product_create_user'):
            raise UserError("Vous ne pouvez pas supprimer des articles. Consulter l'administrateur")
        res = super(ProductTemplate, self).unlink()
        return res