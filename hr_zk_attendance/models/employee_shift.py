# -*- coding: utf-8 -*-

from odoo import models, fields, api


class BaykeeEmployeeShifts(models.Model):
    _name = 'baykee.employee.shift'
    _description = 'Employee Shifts'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name', required=True, tracking=True)
    shift_type = fields.Selection([
        ('Morning', 'Morning'),
        ('Evening', 'Evening'),
        ('Night', 'Night'),
        ('Gazette Morning', 'Gazette Morning'),
        ('Gazette Night', 'Gazette Night'),
    ], string="Shift Type", required=True, tracking=True)
    shift_start = fields.Float('Shift Start', required=True, tracking=True,
                               help="Start and End time of working.\n"
                                    "A specific value of 24:00 is interpreted as 23:59:59.999999.")
    shift_end = fields.Float('Shift End', tracking=True, compute='sum_total', store=True,
                             help="Start and End time of working.\n"
                                  "A specific value of 24:00 is interpreted as 23:59:59.999999.")
    shift_duration = fields.Integer('Shift Duration', tracking=True, default=9,
                                    help="Start and End time of working.\n"
                                         "A specific value of 24:00 is interpreted as 23:59:59.999999.")
    margin = fields.Float('Margin', required=True, tracking=True,
                          help="Start and End time of working.\n"
                               "A specific value of 24:00 is interpreted as 23:59:59.999999.")

    present_end = fields.Float('Present End', tracking=True,
                               help="Start and End time of working.\n"
                                    "A specific value of 24:00 is interpreted as 23:59:59.999999.", compute='sum_total',
                               store=True)
    late_end = fields.Float('Late End', required=True, tracking=True,
                            help="Start and End time of working.\n"
                                 "A specific value of 24:00 is interpreted as 23:59:59.999999.")

    short_leave = fields.Float('Short Leave', required=True, tracking=True,
                               help="Start and End time of working.\n"
                                    "A specific value of 24:00 is interpreted as 23:59:59.999999.")
    half_leave = fields.Float('Half Leave', required=True, tracking=True,
                              help="Start and End time of working.\n"
                                   "A specific value of 24:00 is interpreted as 23:59:59")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('cancel', 'Cancel'),
        ('rejected', 'Rejected')
    ], default='draft', tracking=True)

    """This Function Move to State on Approved """

    def action_approved(self):
        self.state = 'approved'

    """This Function Move to State on Cancel """

    def action_cancel(self):
        self.state = 'cancel'

    """This Function Move to State Reject """

    def action_reject(self):
        self.state = 'rejected'

    """This Function Move to State Draft """

    def action_draft(self):
        self.state = 'draft'

    """This Function is used to Sum of Shift Start and Margin and store it to Present End """

    @api.depends('margin', 'shift_duration', 'shift_start')
    def sum_total(self):
        for rec in self:
            rec.shift_end = 0
            rec.present_end = 0
            if rec.shift_start > 0 or rec.margin:
                rec.present_end = rec.shift_start + rec.margin
                rec.late_end = rec.shift_start + 1
                rec.short_leave = rec.shift_start + 2
            if rec.present_end > 0:
                rec.shift_end = rec.shift_start + rec.shift_duration
                while rec.shift_end >= 24:
                    rec.shift_end -= 24
