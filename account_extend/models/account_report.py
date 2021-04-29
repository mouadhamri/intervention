# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountGeneralLedgerReport(models.AbstractModel):
	_inherit = "account.general.ledger"

	@api.model
	def _get_columns_name(self, options):
		columns_names = super(AccountGeneralLedgerReport, self)._get_columns_name(options)
		columns_names.insert(4, {'name': 'Chantier'})
		return columns_names

	@api.model
	def _get_aml_line(self, options, account, aml, cumulated_balance):
		res = super(AccountGeneralLedgerReport, self)._get_aml_line(options, account, aml, cumulated_balance)
		if res and res.get('columns', False):
			res['columns'].insert(3, {'name': aml['chantier_name'] or ''})
		return res

	@api.model
	def _get_query_amls(self, options, expanded_account, offset = None, limit = None):
		''' Construct a query retrieving the account.move.lines when expanding a report line with or without the load
		        more.
		        :param options:             The report options.
		        :param expanded_account:    The account.account record corresponding to the expanded line.
		        :param offset:              The offset of the query (used by the load more).
		        :param limit:               The limit of the query (used by the load more).
		        :return:                    (query, params)
		        '''

		unfold_all = options.get('unfold_all') or (self._context.get('print_mode') and not options['unfolded_lines'])

		# Get sums for the account move lines.
		# period: [('date' <= options['date_to']), ('date', '>=', options['date_from'])]
		if expanded_account:
			domain = [('account_id', '=', expanded_account.id)]
		elif unfold_all:
			domain = []
		elif options['unfolded_lines']:
			domain = [('account_id', 'in', [int(line[8:]) for line in options['unfolded_lines']])]

		new_options = self._force_strict_range(options)
		tables, where_clause, where_params = self._query_get(new_options, domain = domain)
		ct_query = self.env['res.currency']._get_query_currency_table(options)
		query = '''
		            SELECT
		                account_move_line.id,
		                account_move_line.date,
		                account_move_line.date_maturity,
		                account_move_line.name,
		                account_move_line.ref,
		                account_move_line.company_id,
		                account_move_line.account_id,
		                account_move_line.payment_id,
		                account_move_line.partner_id,
		                account_move_line.currency_id,
		                account_move_line.amount_currency,
		                account_move_line.line_chantier_id, 
		                ROUND(account_move_line.debit * currency_table.rate, currency_table.precision)   AS debit,
		                ROUND(account_move_line.credit * currency_table.rate, currency_table.precision)  AS credit,
		                ROUND(account_move_line.balance * currency_table.rate, currency_table.precision) AS balance,
		                account_move_line__move_id.name         AS move_name,
		                company.currency_id                     AS company_currency_id,
		                partner.name                            AS partner_name,
		                account_move_line__move_id.move_type         AS move_type,
		                account.code                            AS account_code,
		                account.name                            AS account_name,
		                journal.code                            AS journal_code,
		                journal.name                            AS journal_name,
		                full_rec.name                           AS full_rec_name,
		                project.name                            AS chantier_name
		            FROM account_move_line
		            LEFT JOIN account_move account_move_line__move_id ON account_move_line__move_id.id = account_move_line.move_id
		            LEFT JOIN %s ON currency_table.company_id = account_move_line.company_id
		            LEFT JOIN res_company company               ON company.id = account_move_line.company_id
		            LEFT JOIN res_partner partner               ON partner.id = account_move_line.partner_id
		            LEFT JOIN account_account account           ON account.id = account_move_line.account_id
		            LEFT JOIN account_journal journal           ON journal.id = account_move_line.journal_id
		            LEFT JOIN account_full_reconcile full_rec   ON full_rec.id = account_move_line.full_reconcile_id
		            LEFT JOIN project_project  project        ON project.id = account_move_line.line_chantier_id
		            WHERE %s
		            ORDER BY account_move_line.date, account_move_line.id
		        ''' % (ct_query, where_clause)

		if offset:
			query += ' OFFSET %s '
			where_params.append(offset)
		if limit:
			query += ' LIMIT %s '
			where_params.append(limit)

		return query, where_params

	@api.model
	def _get_account_title_line(self, options, account, amount_currency, debit, credit, balance, has_lines):
		res = super(AccountGeneralLedgerReport, self)._get_account_title_line(options, account, amount_currency, debit,
																			  credit, balance, has_lines)
		if res and res.get('columns', False):
			res['columns'].insert(0, {'name': ''})
		return res

	@api.model
	def _get_account_total_line(self, options, account, amount_currency, debit, credit, balance):
		res = super(AccountGeneralLedgerReport, self)._get_account_total_line(options, account, amount_currency, debit,
																			  credit, balance)
		if res and res.get('columns', False):
			res['columns'].insert(0, {'name': ''})
		return res

	@api.model
	def _get_initial_balance_line(self, options, account, amount_currency, debit, credit, balance):
		res = super(AccountGeneralLedgerReport, self)._get_initial_balance_line(options, account, amount_currency, debit,
																				credit, balance)
		if res and res.get('columns', False):
			res['columns'].insert(0, {'name': ''})
		return res


	@api.model
	def _get_total_line(self, options, debit, credit, balance):
		res = super(AccountGeneralLedgerReport, self)._get_total_line(options, debit, credit, balance)
		if res and res.get('columns', False):
			res['columns'].insert(0, {'name': ''})
		return res
