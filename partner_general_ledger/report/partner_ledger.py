# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ReportPartnerLedger(models.AbstractModel):
    _name = 'report.partner_general_ledger.report_partnerledger'

    @api.model
    def _get_report_values(self, docids, data=None):
        partners = data.get('ids',[])
        company = self.env['res.company'].browse(data['company_id'])
        data['company_id'] = company
        data['currency'] = company.currency_id.name
        if partners:
            partner_ids = self.env['res.partner'].browse(data['ids'])
            print('partner_idss', partner_ids)
            data['lines'] = []
            for partner in partner_ids:
                partner_total_credit = 0
                partner_total_debit = 0
                partner_total_10 = 0
                partner_total_20 = 0
                partner_total_55 = 0
                partner_total_7 = 0
                partner_total_196 = 0
                partner_total_EXO = 0
                partner_total_CUMUL = 0

                partner_lines = {'account': partner.property_account_receivable_id.code,
                                 'partner_name': partner.name,
                                 'partner_total_credit' : partner_total_credit,
                                 'partner_total_debit' : partner_total_debit,
                                 'partner_total_10' : partner_total_10,
                                 'partner_total_20' : partner_total_20,
                                 'partner_total_55' : partner_total_55,
                                 'partner_total_7' : partner_total_7,
                                 'partner_total_196' : partner_total_196,
                                 'partner_total_EXO' : partner_total_EXO,
                                 'partner_total_CUMUL' : partner_total_CUMUL,
                                 'partner_lines': []
                                 }
                query = """SELECT a.id, a.journal_id, j.type as journal_type, j.code, a.ref, a.name, a.move_type, a.date, a.amount_total,
                            sum(t10.amount) as partner_total_10,
                            sum(t20.amount) as partner_total_20,
                            sum(t55.amount) as partner_total_55,
                            sum(t7.amount) as partner_total_7,
                            sum(t196.amount) as partner_total_196,
                            sum(t0.amount) as partner_total_0
                            
                            
                            FROM account_move a
							LEFT JOIN account_journal j ON j.id = a.journal_id
							LEFT JOIN account_move_tax_line t10 ON  t10.move_id = a.id AND t10.tax_amount = 10
							LEFT JOIN account_move_tax_line t20 ON t20.move_id = a.id AND t20.tax_amount = 20
							LEFT JOIN account_move_tax_line t55 ON t55.move_id = a.id AND t55.tax_amount = 5.5
							LEFT JOIN account_move_tax_line t7 ON t7.move_id = a.id AND t7.tax_amount = 7
							LEFT JOIN account_move_tax_line t196 ON t196.move_id = a.id AND t196.tax_amount = 19.6
							LEFT JOIN account_move_tax_line t0 ON t0.move_id = a.id AND t0.tax_amount = 0
                            WHERE  
                             a.state = 'posted' and 
                               a.date >=%s and a.date <= %s and a.partner_id = %s
                            GROUP BY a.journal_id, a.id ,j.type, j.code,   a.ref, a.name, a.move_type, a.date   
                            ORDER BY a.date              
                            
                            """
                self._cr.execute(query, (data['date_from'], data['date_to'], partner.id ))
                lines = self._cr.dictfetchall()
                print('linnnnnnnnn', lines)

                for aml in lines:

                    print('aml', aml)
                    line_to_append = aml
                    partner_lines['partner_total_10'] += aml['partner_total_10'] or 0
                    partner_lines['partner_total_20'] += aml['partner_total_20'] or 0
                    partner_lines['partner_total_55'] += aml['partner_total_55'] or 0
                    partner_lines['partner_total_7'] += aml['partner_total_7'] or 0
                    partner_lines['partner_total_196'] += aml['partner_total_196'] or 0
                    partner_lines['partner_total_EXO'] += aml['partner_total_0'] or 0
                    print('rrrrrrrrr', aml['ref'])
                    ref = ''
                    if aml['name'] != None:
                        ref= aml['name']

                    if aml['move_type'] == 'out_invoice':
                        partner_lines['partner_total_debit'] += aml['amount_total']
                        line_to_append['debit'] = aml['amount_total']
                        line_to_append['credit'] =0
                        line_to_append['amount_signed'] =aml['amount_total']
                        line_to_append['libelle'] = 'Facture '+ ref + ' '+ partner.name

                        partner_lines['partner_lines'].append(line_to_append)


                    elif aml['move_type'] == 'out_refund':
                        partner_lines['partner_total_credit'] += aml['amount_total']
                        line_to_append['debit'] = 0
                        line_to_append['credit'] = aml['amount_total']
                        line_to_append['amount_signed'] = (-1) * aml['amount_total']

                        line_to_append['libelle'] = 'Avoir '+ ref + ' '+ partner.name
                        partner_lines['partner_lines'].append(line_to_append)
                    elif aml['move_type'] == 'entry' and aml['journal_type'] in ('bank', 'cash'):
                        partner_lines['partner_total_credit'] += aml['amount_total']
                        line_to_append['debit'] = 0
                        line_to_append['credit'] = aml['amount_total']
                        line_to_append['amount_signed'] = (-1) * aml['amount_total']


                        line_to_append['libelle'] = 'Paiement '+ ref  + ' '+ partner.name
                        partner_lines['partner_lines'].append(line_to_append)



                print('partner_lines', partner_lines)
                data['lines'].append(partner_lines)

        print('dddddddddd2', data['lines'])

        return {
            'doc_ids'  : data['ids'],
            'doc_model': data['model'],
            'docs'     : docids,
            'data'     : data,
        }

