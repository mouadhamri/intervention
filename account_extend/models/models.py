# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.misc import formatLang, format_date, get_lang
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    texte_facturation = fields.Text(string='Texte de Facturation')
    type_facturation = fields.Selection([
        ('manuelle', 'MANUELLE'),
        ('email','PAR EMAIL'),
        ('chorus', 'CHORUS'),
        ], string='Type de Facturation')



class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def default_get(self, default_fields):
        # OVERRIDE
        values = super(AccountMove, self).default_get(default_fields)
        default_soustraitant = self._context.get('default_soustraitant', False)
        if default_soustraitant:
            journal_id = self.env['account.journal'].search(
                    [('journal_sous_traitant', '=', True), ('type', '=', 'purchase'),
                     ])
            if journal_id:
                values.update({'journal_id':journal_id[0].id })


        return values

    @api.model
    def _get_default_journal(self):
        journal = super(AccountMove, self)._get_default_journal()
        default_soustraitant = self._context.get('default_soustraitant', False)
        if default_soustraitant:
            journal_id = self.env['account.journal'].search([('journal_sous_traitant', '=', True), ('type', '=', 'purchase'),
                                                          ])
            if journal_id:
                journal = journal_id[0]

        return journal


    partner_text_facturation = fields.Text(string='Texte de Facturation')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('attente','En Attente de validation'),
        ('posted', 'Open'),
        ('cancel', 'Cancelled')
        ], string='Invoice Status', readonly=True)
    type_facturation = fields.Selection(related='partner_id.type_facturation', store=True)
    show_confirm_button = fields.Boolean(compute='compute_show_confirm_button', store=True)
    followup_required = fields.Boolean(compute='compute_followup_required', string="Relance requise")
    modalite_paiement_id = fields.Many2one('modalite.paiement',string='Modalité de paiement')
    n_siret = fields.Char(string='N° de SIRET', related='partner_id.siret', store=True)
    sale_chantier_id = fields.Many2one('project.project', 'Chantier de BC')
    nom_client_final = fields.Char('Nom/prénom')
    appart_client_final = fields.Char('N° appartement')
    ville_client_final = fields.Char('Ville')
    partner_address_1 = fields.Char("Adresse locataire/particulier")
    tel_client_final = fields.Char('Tél')
    code_postal = fields.Char('Code postal')
    civility = fields.Many2one('res.partner.title', 'Civilité client final')
    text_civility = fields.Many2one('res.partner.title', 'Civilité texte')
    code_service = fields.Char(string='Code Service')
    marche = fields.Char(string='Marché')
    line_chantier_id = fields.Many2one('project.project', compute="compute_line_chantier", store=True, string='Chantier')
    adress3 = fields.Text(string='Adresse 3')


    @api.depends('company_id', 'invoice_filter_type_domain')
    def _compute_suitable_journal_ids(self):
        for m in self:
            print('_compute_suitable_journal_ids', m.invoice_filter_type_domain)
            journal_type = m.invoice_filter_type_domain
            default_soustraitant = self._context.get('default_soustraitant', False)

            company_id = m.company_id.id or self.env.company.id

            if journal_type and  default_soustraitant :
                domain = [('company_id', '=', company_id), ('type', '=', journal_type), ('journal_sous_traitant', '=', True)]
            elif journal_type and not default_soustraitant:
                domain = [('company_id', '=', company_id), ('type', '=', journal_type)]

            else:
                domain = [('company_id', '=', company_id), ('type', 'not in', ('sale', 'purchase'))]

            m.suitable_journal_ids = self.env['account.journal'].search(domain)

    @api.depends('line_ids', 'line_ids.analytic_account_id', 'state')
    def compute_line_chantier(self):
        for rec in self:
            if rec.line_ids:
                if rec.line_ids.filtered(lambda r:r.analytic_account_id) and \
                        len(list(set(rec.line_ids.filtered(lambda r:r.analytic_account_id).mapped('analytic_account_id')))) == 1:

                    line_chantier_id = self.env['project.project'].search([('analytic_account_id', '=', rec.line_ids.mapped('analytic_account_id')[0].id),
                                                                           '|',('active', '=', True), ('active', '=', False)])
                    if line_chantier_id:
                        rec.line_chantier_id = line_chantier_id[0].id
                    else:
                        rec.line_chantier_id = False
                else:
                    rec.line_chantier_id = False
            else:
                rec.line_chantier_id = False




    def get_origin_sale_infos(self):
        for rec in self:
            if rec.invoice_origin:
                origin_sale = self.env['sale.order'].search([('name', '=', rec.invoice_origin)])
                if origin_sale:
                    return origin_sale




    def compute_followup_required(self):
        for rec in self:
            if rec.move_type in  ('out_invoice', 'out_refund', 'out_receipt') and \
                rec.invoice_date_due and rec.invoice_date_due <= fields.Date.context_today(self) and rec.payment_state in ('not_paid', 'partial'):
                rec.followup_required = True
            else:
                rec.followup_required = False

    def action_invoice_followup_sent(self):
        """ Open a window to compose an email, with the edi invoice template
            message loaded by default
        """

        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.ensure_one()
        template= self.env.ref('account_extend.email_template_invoice_followup')
        lang = self.env.context.get('lang')
        # template = self.env['mail.template'].browse(template_id)
        if template.lang:
            lang = template._render_lang(self.ids)[self.id]
        ctx = {
            'default_model': 'account.move',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template),
            'default_template_id': template.id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            # 'custom_layout': "mail.mail_notification_paynow",
            # 'proforma': self.env.context.get('proforma', False),
            'force_email': True,
            'model_description': self.with_context(lang = lang).type_name,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    @api.depends('state', 'move_type')
    def compute_show_confirm_button(self):
        for rec in self:
            rec.show_confirm_button = False
            if rec.move_type in ('out_invoice', 'out_refund', 'out_receipt'):
                if rec.state == 'attente':
                    rec.show_confirm_button = True
                else:
                    rec.show_confirm_button = False
            else:
                if rec.state == 'draft':
                    rec.show_confirm_button = True
                else:
                    rec.show_confirm_button = False


    def action_en_attente(self):
        self.write({'state':'attente'})

    @api.onchange('partner_id')
    def onchange_partner(self):
        if self.partner_id:
            self.partner_text_facturation = self.partner_id and self.partner_id.texte_facturation
            self.modalite_paiement_id = self.partner_id and self.partner_id.modalite_paiement_id and self.partner_id.modalite_paiement_id.id or False

    @api.model_create_multi
    def create(self, vals_list):
        res = super(AccountMove, self).create(vals_list)
        for move in res:
            if move.move_type in ('out_invoice', 'out_refund', 'out_receipt') and move.partner_id:
                move.partner_text_facturation = move.partner_id.texte_facturation
        return res

    def write(self, vals):
        res = super(AccountMove, self).write(vals)
        for rec in self:
            if vals.get('partner_id', False) and not vals.get('partner_text_facturation', False):
                if rec.partner_id.texte_facturation != rec.partner_text_facturation:
                    rec.partner_text_facturation =  rec.partner_id.texte_facturation
        return res


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    line_chantier_id = fields.Many2one('project.project', compute="compute_line_chantier",  store=True)
    unique_tax_id = fields.Many2one('account.tax', compute='compute_unique_tax', store=True)

    @api.depends('tax_ids')
    def compute_unique_tax(self):
        for rec in self:
            if rec.tax_ids and len(rec.tax_ids)==1:
                rec.unique_tax_id = rec.tax_ids[0].id
            else:
                rec.unique_tax_id = False


    @api.depends('analytic_account_id', 'move_id', 'move_id.line_chantier_id')
    def compute_line_chantier(self):
        for rec in self:
            move_project = False

            if rec.analytic_account_id:
                project = self.env['project.project'].search(
                        [('analytic_account_id', '=', rec.analytic_account_id.id),
                         '|', ('active', '=', True), ('active', '=', False)])
                if project:
                    rec.line_chantier_id = project[0].id
                else:
                    rec.line_chantier_id = False
            elif rec.move_id.line_chantier_id:
                rec.line_chantier_id = rec.move_id.line_chantier_id.id
            else:
                rec.line_chantier_id = False

    @api.model_create_multi
    def create(self, vals_list):
        res = super(AccountMoveLine, self).create(vals_list)
        for rec in res:
            if rec.partner_id and rec.partner_id.category_id and  rec.partner_id.category_id.analytic_tag_id:
                rec.write({'analytic_tag_ids':[(4, t.analytic_tag_id.id) for t in rec.partner_id.category_id]})
        return res

    def write(self, vals):
        res = super(AccountMoveLine, self).write(vals)
        if res and vals.get('partner_id', False):
            for rec in self:
                if rec.partner_id and rec.partner_id.category_id and  rec.partner_id.category_id.analytic_tag_id:
                    rec.write({'analytic_tag_ids':[(4, t.analytic_tag_id.id) for t in rec.partner_id.category_id]})
        return res


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        if self.chantier_id:
            res['sale_chantier_id'] = self.chantier_id.id
            res['nom_client_final'] = self.nom_client_final
            res['ville_client_final'] = self.ville_client_final
            res['partner_address_1'] = self.partner_address_1
            res['tel_client_final'] = self.tel_client_final
            res['code_postal'] = self.code_postal
            res['civility'] = self.civility
            res['adress3'] = self.adress3
            res['text_civility'] = self.text_civility and self.text_civility.id or False
        return res


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    journal_sous_traitant = fields.Boolean(string='Facture des sous-traitants')

    def name_get(self):
        res = super(AccountJournal, self).name_get()
        for journal_name in res:
            name = journal_name[1]
            index = res.index(journal_name)
            journal_id = self.env['account.journal'].browse(journal_name[0])

            if journal_id.code:
                name = "(%s) %s" % (journal_id.code, name)
            res[index] = (journal_name[0], name)
        return res


class AccountAnalyticTag(models.Model):
    _inherit = 'account.analytic.tag'

    irremovable = fields.Boolean('A ne pas supprimer', help="Tag utilisaer pour séparrer les partenaires")

    def unlink(self):
        for rec in self:
            if rec.irremovable:
                raise ValidationError('Vous ne pouvez pas supprimer ce tag')
        return super(AccountAnalyticTag, self).unlink()

class ResPartnerCategory(models.Model):
    _inherit = 'res.partner.category'

    analytic_tag_id = fields.Many2one('account.analytic.tag', 'Etiquette analytique')
    irremovable = fields.Boolean('A ne pas supprimer', help="Tag utilisaer pour séparrer les partenaires")

    def unlink(self):
        for rec in self:
            if rec.irremovable:
                raise ValidationError('Vous ne pouvez pas supprimer ce tag')
        return super(ResPartnerCategory, self).unlink()

    @api.model
    def create(self, vals):
        res = super(ResPartnerCategory, self).create(vals)
        if res and not res.analytic_tag_id:
            tag_id = self.env['account.analytic.tag'].sudo().create({'name': res.name})
            res.analytic_tag_id = tag_id.id

        return res

    def write(self, vals):
        res = super(ResPartnerCategory, self).write(vals)
        if res:
            for rec in self:
                if not rec.analytic_tag_id:

                    tag_id = self.env['account.analytic.tag'].create({'name': rec.name})
                    rec.analytic_tag_id = tag_id.id

        return res


