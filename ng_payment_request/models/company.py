from odoo import fields, models, api, _

class res_company(models.Model):
    _inherit = "res.company"
    
    # min_amount = fields.Float('Minimum Amount')
    max_amount = fields.Float('Maximum Amount')