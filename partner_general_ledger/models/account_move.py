# -*- coding: utf-8 -*-

from odoo import api, fields, models

class AccountMove(models.Model):
    _inherit = 'account.move'

    tax_lines = fields.One2many('account.move.tax.line', 'move_id')

    @api.onchange('line_ids', 'invoice_payment_term_id', 'invoice_date_due', 'invoice_cash_rounding_id',
                  'invoice_vendor_bill_id')
    def _onchange_recompute_dynamic_lines(self):
        super(AccountMove, self)._onchange_recompute_dynamic_lines()
        self.compute_tax_lines()


    def compute_tax_lines(self):
        ''' Helper to get the taxes grouped according their account.tax.group.
        This method is only used when printing the invoice.
        '''
        for move in self:
            lang_env = move.with_context(lang = move.partner_id.lang).env
            tax_lines = move.line_ids.filtered(lambda line: line.tax_line_id)
            tax_balance_multiplicator = -1 if move.is_inbound(True) else 1
            res = {}
            # There are as many tax line as there are repartition lines
            done_taxes = set()
            for line in tax_lines:
                res.setdefault(line.tax_line_id.tax_group_id, {'base': 0.0, 'amount': 0.0})
                res[line.tax_line_id.tax_group_id]['amount'] += tax_balance_multiplicator * (
                    line.amount_currency if line.currency_id else line.balance)
                tax_key_add_base = tuple(move._get_tax_key_for_group_add_base(line))
                if tax_key_add_base not in done_taxes:
                    if line.currency_id and line.company_currency_id and line.currency_id != line.company_currency_id:
                        amount = line.company_currency_id._convert(line.tax_base_amount, line.currency_id,
                                                                   line.company_id,
                                                                   line.date or fields.Date.context_today(self))
                    else:
                        amount = line.tax_base_amount
                    res[line.tax_line_id.tax_group_id]['base'] += amount
                    # The base should be added ONCE
                    done_taxes.add(tax_key_add_base)

            # At this point we only want to keep the taxes with a zero amount since they do not
            # generate a tax line.
            zero_taxes = set()
            for line in move.line_ids:
                for tax in line.tax_ids.flatten_taxes_hierarchy():
                    if tax.tax_group_id not in res or tax.tax_group_id in zero_taxes:
                        res.setdefault(tax.tax_group_id, {'base': 0.0, 'amount': 0.0})
                        res[tax.tax_group_id]['base'] += tax_balance_multiplicator * (
                            line.amount_currency if line.currency_id else line.balance)
                        zero_taxes.add(tax.tax_group_id)

            res = sorted(res.items(), key = lambda l: l[0].sequence)
            lines_to_add = []
            if move.tax_lines:
                for group, amounts in res:
                    if group in move.tax_lines.mapped('tax_id'):
                        line = move.tax_lines.filtered(lambda r: r.tax_id == group)
                        line.update({'base': amounts['base'],
                                     'amount':amounts['amount'] })
                    else:
                        lines_to_add.append((0, 0, {'tax_id': group.id,
                                                    'base'  : amounts['base'],
                                                    'amount': amounts['amount']
                                                    }))

            else:
                for group, amounts in res:
                    lines_to_add.append((0, 0, {'tax_id': group.id,
                                                      'base'  : amounts['base'],
                                                      'amount': amounts['amount']
                                                      }))

            if lines_to_add:
                move.update({'tax_lines':lines_to_add})


class AccountMoveTaxLine(models.Model):
    _name= 'account.move.tax.line'

    move_id = fields.Many2one('account.move')
    tax_id = fields.Many2one('account.tax.group')
    tax_amount = fields.Float(compute="compute_tax_amount", store=True)
    amount = fields.Float()
    base = fields.Float()

    @api.depends('tax_id')
    def compute_tax_amount(self):
        for rec in self:
            if rec.tax_id:
                tax = self.env['account.tax'].search([('tax_group_id', '=', rec.tax_id.id)])
                if tax:
                    rec.tax_amount = tax[0].amount