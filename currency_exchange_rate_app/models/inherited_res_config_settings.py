# -*- coding: utf-8 -*-
from odoo import models, fields, api,_


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    
    currency_exchange = fields.Selection([('normal_currency_exchange','Normal Currency Exchange'),('inverse_currency_exchange','Inverse Currency Exchange')],
                        string='Exchange Currency Selection', related="company_id.currency_exchange" ,readonly=False)



class ResCompany(models.Model):
    _inherit = "res.company"

    currency_exchange = fields.Selection([('normal_currency_exchange','Normal Currency Exchange'),('inverse_currency_exchange','Inverse Currency Exchange')],
                        string='Exchange Currency Selection' ,readonly=False)