 # -*- coding: utf-8 -*-


from odoo.tools.misc import formatLang, get_lang
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class InheritedSaleOrder(models.Model):
	_inherit = 'sale.order'

	order_currency_id = fields.Many2one('res.currency', string='Order Currency', tracking=True)
	apply_currency_exchange = fields.Boolean(string='Apply Currency Exchange', tracking=True, copy=False)
	currency_exchange_rate = fields.Float(string='Currency Exchange Rate', tracking=True, copy=False)

	def _prepare_invoice(self):
		invoice_vals = super(InheritedSaleOrder, self)._prepare_invoice()
		if invoice_vals:
			if self.apply_currency_exchange:
				if self.order_currency_id.id:
					invoice_vals['order_currency_id'] = self.order_currency_id.id
				if self.apply_currency_exchange:
					invoice_vals['apply_currency_exchange'] = self.apply_currency_exchange
				if self.currency_exchange_rate:
					invoice_vals['currency_exchange_rate'] = self.currency_exchange_rate
				if self.order_currency_id.id:
					invoice_vals['currency_id'] = self.order_currency_id.id
		return invoice_vals

	def _create_invoices(self, grouped=False, final=False, date=None):
		moves = super(InheritedSaleOrder, self)._create_invoices(grouped=grouped, final=final, date=date)
		if moves:
			if self.apply_currency_exchange:
				moves._compute_currency_id()
		return moves
