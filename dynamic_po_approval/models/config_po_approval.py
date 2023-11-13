# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright 2019 EquickERP
#
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import Warning


class res_company(models.Model):
    _inherit = 'res.company'

    config_po_approval_ids = fields.One2many(comodel_name='config.po.approval', inverse_name='company_id', string="Approval Configuration")

    @api.constrains('config_po_approval_ids')
    def check_company_min_max_amount_overlap(self):
        config_obj = self.env['config.po.approval']
        for company in self:
            for config in company.config_po_approval_ids:
                if not config.max_amount:
                    raise Warning(_("Please enter to amount."))
                if config.min_amount > config.max_amount:
                    raise Warning(_("From amount should be less than To amount."))
                other_config_ids = config_obj.search([('company_id', '=', company.id),
                                                      ('id', '!=', config.id),
                                                      ('min_amount', '<=', config.max_amount),
                                                      ('max_amount', '>=', config.min_amount)])
                if other_config_ids:
                    raise Warning(_("From and To amount must not overlap. Please correct it."))
                if not config.approval_line_ids:
                    raise Warning(_("Please enter at least one Approval Level line."))


class config_po_approval(models.Model):
    _name = 'config.po.approval'
    _description = 'Purchase order Approval Configuration'
    _order = 'min_amount, max_amount'

    company_id = fields.Many2one(comodel_name='res.company', string="Company Ref")
    currency_id = fields.Many2one(related='company_id.currency_id', depends=['company_id.currency_id'], store=True, string='Currency', readonly=True)
    min_amount = fields.Monetary(string="From Amount", currency_field='currency_id', required=1)
    max_amount = fields.Monetary(string="To Amount", currency_field='currency_id', required=1)
    approve_by = fields.Selection(selection=[('user', 'User'),
                                             ('group', 'Group')], string="Approve Process By", required=1)
    approval_line_ids = fields.One2many(comodel_name='config.po.approval.line', inverse_name='config_approval_id', string="Approve Line ref")

    @api.onchange('approve_by')
    def onchange_approve_by_option(self):
        self.approval_line_ids = False


class config_po_approval_line(models.Model):
    _name = 'config.po.approval.line'
    _description = 'Purchase order Approval Configuration Line'
    _order = 'sequence, id'

    sequence = fields.Integer(string="Level")
    res_group_id = fields.Many2one(comodel_name='res.groups', string="Group")
    res_user_ids = fields.Many2many(comodel_name='res.users', string="User(s)")
    config_approval_id = fields.Many2one(comodel_name='config.po.approval', string="Config Ref",ondelete='cascade')

    @api.constrains('res_user_ids','res_group_id','sequence')
    def check_unique_sequence(self):
        for line in self:
            if line.sequence < 0:
                raise Warning(_("Level should be positive number."))
            if line.config_approval_id.approval_line_ids.filtered(lambda l:l.id != line.id and l.sequence == line.sequence):
                raise Warning(_("Level should be unique for each approval."))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: