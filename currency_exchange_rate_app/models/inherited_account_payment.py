# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class InheritedAccountPaymentRegister(models.TransientModel):
	_inherit = 'account.payment.register'

	order_currency_id = fields.Many2one('res.currency', string='Order Currency')
	apply_currency_exchange = fields.Boolean(string='Apply Currency Exchange')
	currency_exchange_rate = fields.Float(string='Currency Exchange Rate')


	@api.model
	def default_get(self, fields_list):
		# OVERRIDE
		res = super().default_get(fields_list)
		active_id = self.env.context.get('active_id')
		move_id = self.env['account.move'].browse(active_id)
		if res:
			# if move_id.company_id.currency_id.id:
			# 	res['currency_id'] = move_id.company_id.currency_id.id
			if move_id.order_currency_id:
				res['order_currency_id'] = move_id.order_currency_id.id
			if move_id.apply_currency_exchange:
				res['apply_currency_exchange'] = move_id.apply_currency_exchange
			if move_id.currency_exchange_rate:
				res['currency_exchange_rate'] = move_id.currency_exchange_rate
		return res

	def _create_payment_vals_from_wizard(self, batch_result):
		payment_vals = super(InheritedAccountPaymentRegister, self)._create_payment_vals_from_wizard(batch_result)
		if payment_vals:
			# if self.company_id.currency_id.id:
			# 	payment_vals['currency_id'] = self.company_id.currency_id.id
			if self.order_currency_id.id:
				payment_vals['order_currency_id'] = self.order_currency_id.id
			if self.apply_currency_exchange:
				payment_vals['apply_currency_exchange'] = self.apply_currency_exchange
			if self.currency_exchange_rate:
				payment_vals['currency_exchange_rate'] = self.currency_exchange_rate
		return payment_vals

	@api.depends('can_edit_wizard', 'source_amount', 'source_amount_currency', 'source_currency_id', 'company_id', 'currency_id', 'payment_date', 'apply_currency_exchange', 'order_currency_id')
	def _compute_amount(self):
		for wizard in self:
			if wizard.apply_currency_exchange and wizard.order_currency_id:
				wizard.currency_id = wizard.order_currency_id 
			if wizard.source_currency_id and wizard.can_edit_wizard:
				batch_result = wizard._get_batches()[0]
				wizard.amount = wizard._get_total_amount_in_wizard_currency_to_full_reconcile(batch_result)[0]
			else:
				# The wizard is not editable so no partial payment allowed and then, 'amount' is not used.
				wizard.amount = None


class InheritedAccountPayment(models.Model):
	_inherit = 'account.payment'

	order_currency_id = fields.Many2one('res.currency', string='Order Currency')
	apply_currency_exchange = fields.Boolean(string='Apply Currency Exchange')
	currency_exchange_rate = fields.Float(string='Currency Exchange Rate')


	@api.model
	def default_get(self, default_fields):
		rec = super(InheritedAccountPayment, self).default_get(default_fields)
		active_ids = self._context.get('active_ids') or self._context.get('active_id')
		active_model = self._context.get('active_model')

		# Check for selected invoices ids
		if not active_ids or active_model != 'account.move':
			return rec
		invoices = self.env['account.move'].browse(active_ids).filtered(
			lambda move: move.is_invoice(include_receipts=True))
		for move in invoices:
			if move.apply_currency_exchange:
				rec.update({
					'apply_currency_exchange': move.apply_currency_exchange,
					'currency_exchange_rate': move.currency_exchange_rate,
					'order_currency_id': move.order_currency_id.id,
				})
		return rec


	def _prepare_move_line_default_vals(self, write_off_line_vals=None):
		''' Prepare the dictionary to create the default account.move.lines for the current payment.
		:param write_off_line_vals: Optional list of dictionaries to create a write-off account.move.line easily containing:
			* amount:       The amount to be added to the counterpart amount.
			* name:         The label to set on the line.
			* account_id:   The account on which create the write-off.
		:return: A list of python dictionary to be passed to the account.move.line's 'create' method.
		'''
		self.ensure_one()
		write_off_line_vals = write_off_line_vals or {}

		if not self.outstanding_account_id:
			raise UserError(_(
				"You can't create a new payment without an outstanding payments/receipts account set either on the company or the %s payment method in the %s journal.",
				self.payment_method_line_id.name, self.journal_id.display_name))

		# Compute amounts.
		write_off_line_vals_list = write_off_line_vals or []
		write_off_amount_currency = sum(x['amount_currency'] for x in write_off_line_vals_list)
		write_off_balance = sum(x['balance'] for x in write_off_line_vals_list)

		if self.payment_type == 'inbound':
			# Receive money.
			liquidity_amount_currency = self.amount
		elif self.payment_type == 'outbound':
			# Send money.
			liquidity_amount_currency = -self.amount
		else:
			liquidity_amount_currency = 0.0

		liquidity_balance = self.currency_id._convert(
			liquidity_amount_currency,
			self.company_id.currency_id,
			self.company_id,
			self.date,
		)
		counterpart_amount_currency = -liquidity_amount_currency - write_off_amount_currency
		counterpart_balance = -liquidity_balance - write_off_balance
		currency_id = self.currency_id.id

		if self.env.user.company_id.currency_exchange == 'normal_currency_exchange':
			if self.apply_currency_exchange:
				currency_id = self.order_currency_id.id
				currency_rate = self.currency_exchange_rate
				liquidity_balance = liquidity_amount_currency * currency_rate
				write_off_balance = write_off_amount_currency * currency_rate
				counterpart_balance = -liquidity_balance - write_off_balance
		if self.env.user.company_id.currency_exchange == 'inverse_currency_exchange':
			if self.apply_currency_exchange:
				currency_id = self.order_currency_id.id
				currency_rate = self.currency_exchange_rate
				liquidity_balance = liquidity_amount_currency / currency_rate
				write_off_balance = write_off_amount_currency / currency_rate
				counterpart_balance = -liquidity_balance - write_off_balance

		# Compute a default label to set on the journal items.
		liquidity_line_name = ''.join(x[1] for x in self._get_liquidity_aml_display_name_list())
		counterpart_line_name = ''.join(x[1] for x in self._get_counterpart_aml_display_name_list())

		line_vals_list = [
			# Liquidity line.
			{
				'name': liquidity_line_name,
				'date_maturity': self.date,
				'amount_currency': liquidity_amount_currency,
				'currency_id': currency_id,
				'debit': liquidity_balance if liquidity_balance > 0.0 else 0.0,
				'credit': -liquidity_balance if liquidity_balance < 0.0 else 0.0,
				'partner_id': self.partner_id.id,
				'account_id': self.outstanding_account_id.id,
			},
			# Receivable / Payable.
			{
				'name': counterpart_line_name,
				'date_maturity': self.date,
				'amount_currency': counterpart_amount_currency,
				'currency_id': currency_id,
				'debit': counterpart_balance if counterpart_balance > 0.0 else 0.0,
				'credit': -counterpart_balance if counterpart_balance < 0.0 else 0.0,
				'partner_id': self.partner_id.id,
				'account_id': self.destination_account_id.id,
			},
		]
		return line_vals_list + write_off_line_vals_list