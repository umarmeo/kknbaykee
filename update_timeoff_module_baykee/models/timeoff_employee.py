import datetime
import logging
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.translate import _
from odoo.tools.float_utils import float_round
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)

AVAILABLE_PRIORITIES = [
    ('0', 'Low'),
    ('1', 'Medium'),
    ('2', 'High'),
    ('3', 'Very High'),
]


class EachTimeoffEmployeeForm(models.Model):
    _name = 'hr.leave.employee'
    _description = 'HR Leave Employee'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    color = fields.Integer('Color Index')
    kanban_state = fields.Selection([
        ('normal', 'Grey'),
        ('done', 'Green'),
        ('blocked', 'Red')], string='Kanban State',
        copy=False, default='normal', required=True)
    priority = fields.Selection(AVAILABLE_PRIORITIES, string='Priority', index=True, default=AVAILABLE_PRIORITIES[0][0])

    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]

    company_type = fields.Selection([
        ('Employee', 'Employee'),
        ('Company', 'Company'),
    ], default='Employee', string="Company Type", tracking=True)
    department_id = fields.Many2one('hr.department', string='Department',
                                    default=lambda self: self.env['hr.department'].search(
                                        [('manager_id.user_id', '=', self.env.user.id)], limit=1).id, tracking=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', tracking=True)

    leave_type = fields.Many2one('hr.leave.type', required=1, string="Leave Type", tracking=True,
                                 domain="[('name', 'in', ('Unpaid Leaves', 'Marriage Leaves', 'Paid Leaves', 'Blood Relation Death Leaves'))]")
    leave_type_name = fields.Char(related='leave_type.name')
    is_portal = fields.Boolean('Portal Entry')
    sub_leave_type = fields.Selection([
        ('day', 'FulL Day'),
        ('half', 'Half Leave'),
        ('short', 'Short Leave'),
    ], string='Types', default='day')
    date_from = fields.Date('From', tracking=True)
    date_to = fields.Date('To', tracking=True)

    datetime_from = fields.Datetime('From', tracking=True)
    datetime_to = fields.Datetime('To', tracking=True)
    halfday_type = fields.Selection([('1st Half', '1st Half'), ('2nd Half', '2nd Half')], string="Half Leave",
                                    tracking=True)
    shortday_type = fields.Selection([('1', '1st Slot (Check-In)'),
                                      ('2', '2nd Slot'),
                                      ('3', '3rd Slot'),
                                      ('4', '4th Slot (Check-Out)')], string="Short Leave (Slot)",
                                     tracking=True)

    duration = fields.Float('DURATION', required=1, default=1.0, tracking=True)
    name = fields.Char('DESCRIPTION', required=1, tracking=True)
    state = fields.Selection([
        ('Draft', 'Draft'),
        ('Manager Approval', 'Manager Approval'),
        ('HR Approval', 'HR Approval'),
        ('COO Approval', 'COO Approval'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Cancel', 'Cancel'),
    ], string='State', required=1, group_expand='_expand_states', default='Draft', tracking=True)
    auto_approve = fields.Boolean()
    total_leave_summary = fields.One2many('hr.leave.employee.report', 'employee_leave', tracking=True)
    leave_id = fields.Many2one('hr.leave', tracking=True)
    types = fields.Selection([
        ('Timeoff', 'Timeoff'),
        ('Allocation', 'Allocation'),
    ], string='Types')
    number_of_days = fields.Integer('Duration', default=1)
    leave_report = fields.Many2many('hr.leave')
    cancel_reason = fields.Char('Reject Remarks', readonly=True, tracking=True)

    def cancel_button(self, reason=False, cancel=False):
        if cancel:
            self.cancel_reason = reason
            self.state = 'Cancel'

    def get_portal_url(self):
        if self.types == 'Allocation':
            action = self.env.ref('update_timeoff_module_baykee.action_allocation_leaves').id
        else:
            action = self.env.ref('update_timeoff_module_baykee.action_timeoff_leaves').id
        portal_link = "{}/web?db={}#id={}&view_type=form&model={}&action={}".format(
            self.env['ir.config_parameter'].sudo().get_param('web.base.url'), self.env.cr.dbname, self.id, self._name,
            action)
        return portal_link

    @api.onchange('sub_leave_type')
    def _onchange_dsub_leave_type(self):
        self.date_to = False
        self.date_from = False
        self.datetime_from = False
        self.datetime_to = False
        if self.sub_leave_type == 'short' and self.date_from:
            self.date_to = self.date_from
            self.duration = 0.25
        elif self.sub_leave_type == 'half' and self.date_from:
            self.date_to = self.date_from
            self.duration = 0.5

    @api.onchange('date_from', 'date_to')
    def _onchange_date_difference(self):
        if self.date_from and self.date_to:
            duration = (self.date_to - self.date_from)
            self.duration = duration.days + 1
            if self.sub_leave_type == 'short' and self.date_from:
                self.date_to = self.date_from
                self.duration = 0.25
            elif self.sub_leave_type == 'half' and self.date_from:
                self.date_to = self.date_from
                self.duration = 0.5
            if self.date_from > self.date_to:
                raise ValidationError('From Date must be less than To Date')
            if self.leave_type.name == 'Short Leave':
                self.sub_leave_type = 'short'
                self.duration = 1.0
            if self.leave_type.name == 'Half Leave':
                self.sub_leave_type = 'half'
                self.duration = 1.0

    @api.onchange('datetime_from', 'datetime_to')
    def _onchange_datetime_difference(self):
        if self.datetime_from and self.datetime_to:
            if self.datetime_from > self.datetime_to:
                raise ValidationError('From Date must be less than To Date')
            duration = (self.datetime_to - self.datetime_from)
            days, seconds = duration.days, duration.seconds
            hours = days * 24 + seconds // 3600
            if days > 0:
                raise ValidationError('Short leave can apply only for 2 hours')
            if hours > 2:
                raise ValidationError('Short leave can apply only for 2 hours')
            # self.duration = duration.days
            if self.sub_leave_type == 'short' and self.datetime_from:
                self.date_from = self.datetime_from.date()
                self.date_to = self.datetime_from.date()
                self.duration = 0.25
            if self.leave_type.name == 'Short Leave':
                self.sub_leave_type = 'short'
                self.duration = 1.0
            if self.leave_type.name == 'Half Leave':
                self.sub_leave_type = 'half'
                self.duration = 1.0
            # self._onchange_allocated_leaves_check()

    @api.onchange('date_from', 'date_to', 'department_id', 'duration', 'state')
    def _onchange_date_domain_check(self):
        res = {}

        if self.sub_leave_type == 'short' and self.date_from:
            self.date_to = self.date_from
            self.duration = 0.25
        elif self.sub_leave_type == 'half' and self.date_from:
            self.date_to = self.date_from
            self.duration = 0.5
        if self.leave_type.name == 'Short Leave':
            self.sub_leave_type = 'short'
            self.duration = 1.0
        if self.leave_type.name == 'Half Leave':
            self.sub_leave_type = 'half'
            self.duration = 1.0
        if self.env.user.has_group('update_timeoff_module_baykee.group_leaves_attendance_own'):
            if self.department_id:
                res['domain'] = {"employee_id": ['|', '|',
                                                 ('department_id.manager_id', '=', self.department_id.manager_id.id),
                                                 ('parent_id', '=', self.department_id.manager_id.id),
                                                 ('id', '=', self.department_id.manager_id.id)
                                                 ]
                                 }
                return res

    @api.onchange('number_of_days')
    def _onchange_number_of_days_check(self):
        if self.number_of_days <= 0:
            raise ValidationError('Duration must be greater than 0')

    @api.onchange('leave_type')
    def _onchange_allocated_leaves_check_new(self):
        self.sub_leave_type = 'day'
        if self.leave_type.name == 'Short Leave':
            self.sub_leave_type = 'short'
            self.duration = 1.0
        if self.leave_type.name == 'Half Leave':
            self.sub_leave_type = 'half'
            self.duration = 1.0

        self.halfday_type = False
        self.shortday_type = False
        self.date_from = False
        self.date_to = False
        self.duration = 1.0

    @api.onchange('leave_type')
    def _onchange_allocated_leaves_check(self):
        if self.leave_type and self.types == 'Timeoff' and self.company_type == 'Employee':
            available = 0
            short_leave_balance = 0
            half_leave_balance = 0
            for record in self.total_leave_summary:
                if record.leave_type.ids[0] == self.leave_type.ids[0]:
                    available = record.available
                if record.leave_type.name == 'Short Leave':
                    short_leave_balance = record.available
                if record.leave_type.name == 'Half Leave':
                    half_leave_balance = record.available
            if float(available) == 0 and self.leave_type.name not in (
                    'Official Leaves', 'Unpaid Leaves', 'Wedding Leaves', 'Umrah Leaves'):
                raise ValidationError('No Balance Available for this leave')
            if float(available) < self.duration and self.leave_type.name not in (
                    'Official Leaves', 'Unpaid Leaves', 'Wedding Leaves', 'Umrah Leaves'):
                raise ValidationError('No Balance Available for this leave')
            # if self.employee_id.job_status == 'PROBATION' and \
            #         self.leave_type.name in ('Sick Leaves', 'Casual Leaves', 'Annual Leaves'):
            #     raise ValidationError('Probation Employee cannot use Sick Leaves, Casual Leaves, Annual Leaves')
            if self.is_portal is False and self.leave_type.name in ('Short Leave', 'Half Leave'):
                self.sub_leave_type = 'day'
                if self.leave_type.name == 'Short Leave':
                    self.sub_leave_type = 'short'
                    if float(half_leave_balance) == 0:
                        raise ValidationError(
                            'You already use half leave you are not allowed to use short leave anymore')
                if self.leave_type.name == 'Half Leave':
                    self.sub_leave_type = 'half'
                    if float(short_leave_balance) < 2:
                        raise ValidationError(
                            'You already use short leave you are not allowed to use half leave anymore')

    @api.onchange('employee_id')
    def _onchange_allocated_leaves(self):
        self.leave_type = False
        if self.employee_id:
            self.department_id = self.employee_id.department_id.id
            query = """select leave.name, sum(report.number_of_days), case when leave.leave_type_days = 'monthly'
            then leave.days_monthly_leave else leave.days_annual_leave end, leave.id, leave.no_of_year from hr_leave_report as report 
            INNER JOIN hr_leave_type as leave ON leave.id = report.holiday_status_id 
            where report.state = 'validate' and employee_id={} group by leave.name, leave.id;
            """.format(str(self.employee_id.ids[0]))
            self.env.cr.execute(query)
            employee_ids = self.env.cr.fetchall()
            lines = [(5, 0, 0)]

            for employee in employee_ids:
                if employee[1] >= 0:
                    vals = {
                        'name': employee[0],
                        'available': employee[1],
                        'allocated': employee[2] * employee[4] if employee[2] is not None else employee[1],
                        'leave_type': employee[3],
                    }
                    lines.append((0, 0, vals))
            self.total_leave_summary = lines
            self.department_id = self.employee_id.department_id.id
            self.leave_report = self.env['hr.leave'].search(
                [('employee_id', '=', self.employee_id.id), ('state', '=', 'validate')])

    def request_manager(self):
        if self.company_type == 'Employee':
            if self.employee_id:
                if self.leave_type.name in ('Casual Leaves', 'Annual Leaves'):
                    if self.date_from < datetime.date.today():
                        raise ValidationError('You can only apply for Pre leave')
                    if self.date_from <= datetime.date.today() and self.leave_type.name == 'Annual Leaves':
                        raise ValidationError('You can only apply for Pre leaves')
                    employees = self.env['hr.leave.employee'].search([('employee_id', '=', self.employee_id.ids[0]),
                                                                      ('id', '!=', self.ids[0]),
                                                                      ('leave_type', '=', self.leave_type.id),
                                                                      ('state', 'in', (
                                                                          'Approved', 'Manager Approval', 'HR Approval',
                                                                          'Draft',
                                                                          'COO Approval')),
                                                                      (
                                                                      'date_from', '>=', self.date_from.replace(day=1)),
                                                                      ('date_from', '<=',
                                                                       self.date_from.replace(day=1) + relativedelta(
                                                                           months=1) - datetime.timedelta(days=1))])
                    duration = self.duration
                    for employee in employees:
                        duration += employee.duration
                    if self.leave_type.name == 'Casual Leaves' and duration > 2:
                        raise ValidationError('You cannot apply more than 2 Casual Leaves')
                    if self.leave_type.name == 'Annual Leaves' and self.duration < 7:
                        raise ValidationError('You cannot apply less than 7 Annual Leaves')
                    if self.leave_type.name == 'Annual Leaves' and self.date_from:
                        difference = self.date_from - datetime.date.today()
                        if difference.days < 15:
                            raise ValidationError('You have to apply Annual Leaves before 15 days')

                self._onchange_allocated_leaves_check()
                MailTemplate = self.env.ref('update_timeoff_module_baykee.employee_manager_leave_approval_hr', False)
                if self.employee_id.work_email:
                    email = self.employee_id.work_email
                else:
                    email = 'sys@kknetworks.com.pk'
                if self.employee_id.ids[0] == self.department_id.manager_id.ids[0]:
                    email_to = self.employee_id.parent_id.work_email
                else:
                    email_to = self.department_id.manager_id.work_email
                MailTemplate.sudo().write({'email_from': email, 'email_to': email_to})
                MailTemplate.sudo().send_mail(self.ids[0], force_send=True)
                self.state = 'Manager Approval'
        else:
            if self.leave_type.name == 'Gazette Holiday':
                self.create_leave_in_system_company(changing=True)
                self.state = 'Approved'
            else:
                raise ValidationError('You can mark only Gazette Holiday')

    def request_complete(self):
        if self.company_type == 'Employee':
            if self.employee_id:
                if self.employee_id.ids[0] == self.department_id.manager_id.ids[0]:
                    if len(self.employee_id.parent_id.user_id) == 1:
                        if self.employee_id.parent_id.user_id.ids[0] != self.env.user.ids[0]:
                            raise ValidationError('Related Manager can approve this.')
                    else:
                        raise ValidationError('Related Manager can approve this.')
                elif len(self.employee_id.parent_id.user_id) == 1:
                    if self.employee_id.parent_id.user_id.ids[0] != self.env.user.ids[0] and \
                            self.department_id.manager_id.user_id.ids[0] != self.env.user.ids[0]:
                        raise ValidationError('Related Team Lead / Department Manager can change this.')
                else:
                    if self.department_id.manager_id.user_id.ids[0] != self.env.user.ids[0]:
                        raise ValidationError('Related Team Lead / Department Manager can change this.')
                self.state = 'HR Approval'

    def request_complete_system(self):
        if self.employee_id:
            human_department_id = self.env['hr.department'].search(
                [('name', '=', 'HUMAN RESOURCE'), ('company_id', '=', self.env.company.id)], limit=1)
            MailTemplate = self.env.ref('update_timeoff_module_baykee.email_attendance_approval_hr', False)
            MailTemplate.sudo().write({'email_cc': human_department_id.manager_id.work_email})

            MailTemplate.sudo().send_mail(self.ids[0], force_send=True)
            self.state = 'HR Approval'
        else:
            if self.leave_type.name == 'Gazette Holiday':
                self.create_leave_in_system_company(changing=True)
                self.state = 'Approved'
            else:
                raise ValidationError('You can mark only Gazette Holiday')

    def request_manager_allocation(self):
        if self.employee_id:
            if self.leave_type.name in ('Marriage Leaves', 'Blood Relation Death Leaves'):
                raise ValidationError('You cannot request for this allocation')
            self.state = 'Manager Approval'

    def request_complete_allocation(self):
        if self.employee_id:
            if self.leave_type.name in ('Marriage Leaves', 'Blood Relation Death Leaves'):
                raise ValidationError('You cannot request for this allocation')
            if self.employee_id.ids[0] == self.department_id.manager_id.ids[0]:
                print(len(self.employee_id.parent_id.user_id), 'yos')
                if len(self.employee_id.parent_id.user_id) == 1:
                    if self.employee_id.parent_id.user_id.ids[0] != self.env.user.ids[0]:
                        raise ValidationError('Related Manager can approve this.')
                else:
                    raise ValidationError('Related Manager can approve this.')
            elif len(self.employee_id.parent_id.user_id) == 1:
                if self.employee_id.parent_id.user_id.ids[0] != self.env.user.ids[0] and \
                        self.department_id.manager_id.user_id.ids[0] != self.env.user.ids[0]:
                    raise ValidationError('Related Team Lead / Department Manager can change this.')
            else:
                if self.department_id.manager_id.user_id.ids[0] != self.env.user.ids[0]:
                    raise ValidationError('Related Team Lead / Department Manager can change this.')
            # human_department_id = self.env['hr.department'].search(
            #     [('name', '=', 'HUMAN RESOURCE'), ('company_id', '=', self.env.company.id)], limit=1)
            # MailTemplate = self.env.ref('update_timeoff_form.email_attendance_approval_hr', False)
            # MailTemplate.sudo().write({'email_cc': human_department_id.manager_id.work_email})
            #
            # MailTemplate.sudo().send_mail(self.ids[0], force_send=True)
            self.state = 'HR Approval'

    def manager_complete_allocation(self):
        if self.employee_id:
            self.department_id = self.employee_id.department_id.id
            human_department_id = self.env['hr.department'].search(
                [('name', '=', 'HUMAN RESOURCE'), ('company_id', '=', self.env.company.id)], limit=1)
            MailTemplate = self.env.ref('update_timeoff_module_baykee.email_attendance_manager_department_new', False)
            MailTemplate.sudo().write({'email_cc': human_department_id.manager_id.work_email})
            MailTemplate.sudo().send_mail(self.ids[0], force_send=True)
            query = """
            select leave.name, sum(report.number_of_days), case when leave.leave_type_days = 'monthly'
            then leave.days_monthly_leave else leave.days_annual_leave end, leave.id, leave.no_of_year from hr_leave_report as report 
            INNER JOIN hr_leave_type as leave ON leave.id = report.holiday_status_id 
            where report.state = 'validate' and employee_id={} group by leave.name, leave.id;
            """.format(str(self.employee_id.ids[0]))

            self.env.cr.execute(query)
            employee_ids = self.env.cr.fetchall()
            lines = [(5, 0, 0)]

            for employee in employee_ids:
                if employee[1] >= 0:
                    vals = {
                        'name': employee[0],
                        'available': employee[1],
                        'allocated': employee[2] * employee[4] if employee[2] is not None else employee[1],
                        'leave_type': employee[3],
                    }
                    lines.append((0, 0, vals))
            self.total_leave_summary = lines
            self.leave_report = self.env['hr.leave'].search(
                [('employee_id', '=', self.employee_id.id), ('state', '=', 'validate')])
            self.department_id = self.employee_id.department_id.id

    def request_for_coo_approval_allocation(self):
        if self.employee_id:
            self.state = 'COO Approval'

    def request_approved_allocation(self):
        if self.employee_id:
            self.create_leave_allocation_in_system(changing=True)
            self.state = 'Approved'

    def request_reject_allocation(self):
        if self.employee_id:
            self.state = 'Rejected'

    def request_for_coo_approval(self):
        self.state = 'COO Approval'

    def request_approved(self):
        if self.employee_id:
            self.create_leave_in_system(changing=True)
            self.state = 'Approved'

    def request_reject(self):
        if self.employee_id:
            self.state = 'Rejected'

    def create_leave_in_system(self, changing=False):
        if changing:
            query = "update ir_model_access set perm_write=true,perm_create=true where name='hr.attendance.edit.attendance';"
            self.env.cr.execute(query)
            status = '3'
            if self.leave_type.name in ('Sick Leaves', 'Casual Leaves', 'Short Leave', 'Half Leave'):
                if self.sub_leave_type == 'half':
                    if self.halfday_type == '1st Half':
                        status = '1'
                    else:
                        status = '2'
                elif self.sub_leave_type == 'short':
                    if self.shortday_type == '1':
                        status = '1'
                    elif self.shortday_type == '4':
                        status = '2'
                    else:
                        status = '0'
            vals = {
                'holiday_status_id': self.leave_type.ids[0],
                'request_date_from': self.date_from,
                'request_date_to': self.date_to,
                'holiday_type': 'employee',
                'employee_id': self.employee_id.ids[0],
                'department_id': self.department_id.ids[0],
                'number_of_days': self.duration,
                'name': self.name,
                'report_note': status,
            }
            leave = self.env['hr.leave'].create(vals)
            leave.action_approve()
            leave.action_validate()
            self.leave_id = leave.id
            query = "update ir_model_access set perm_write=false,perm_create=false where name='hr.attendance.edit.attendance';"
            self.env.cr.execute(query)

    def create_leave_allocation_in_system(self, changing=False):
        if changing:
            query = "update ir_model_access set perm_write=true,perm_create=true where name='hr.attendance.edit.attendance';"
            self.env.cr.execute(query)
            vals = {
                'holiday_type': 'employee',
                'employee_id': self.employee_id.ids[0],
                'name': self.name,
                'allocation_type': 'regular',
                'holiday_status_id': self.leave_type.ids[0],
                'number_of_days': self.number_of_days,
                'number_of_days_display': self.number_of_days,
            }
            casual_allocate = self.env['hr.leave.allocation'].create(vals)
            casual_allocate.action_confirm()
            casual_allocate.action_validate()
            query = "update ir_model_access set perm_write=false,perm_create=false where name='hr.attendance.edit.attendance';"
            self.env.cr.execute(query)

    def create_leave_in_system_company(self, changing=False):
        if changing:
            query = "update ir_model_access set perm_write=true,perm_create=true where name='hr.attendance.edit.attendance';"
            self.env.cr.execute(query)
            employees = self.env['hr.employee'].search([('name', '!=', 'System')])
            for employee in employees:
                vals = {
                    'holiday_status_id': self.leave_type.ids[0],
                    'request_date_from': self.date_from,
                    'request_date_to': self.date_to,
                    'holiday_type': 'employee',
                    'employee_id': employee.ids[0],
                    'department_id': employee.department_id.ids[0],
                    'number_of_days': self.duration,
                    'name': self.name,
                }
                leave = self.env['hr.leave'].create(vals)
                leave.action_approve()
                self.leave_id = leave.id
            query = "update ir_model_access set perm_write=false,perm_create=false where name='hr.attendance.edit.attendance';"
            self.env.cr.execute(query)

    def send_leave_in_manager_department(self, changing=False):
        if changing:
            if self.employee_id:
                if self.leave_type.name == 'Short Leave':
                    self.sub_leave_type = 'short'
                    self.duration = 1.0
                if self.leave_type.name == 'Half Leave':
                    self.sub_leave_type = 'half'
                    self.duration = 1.0
                if self.datetime_from and self.datetime_to:
                    duration = (self.datetime_to - self.datetime_from)
                    days, seconds = duration.days, duration.seconds
                    hours = days * 24 + seconds // 3600
                    # minutes = (seconds % 3600) // 60
                    # seconds = seconds % 60
                    if days > 0:
                        raise ValidationError('Short leave can apply only for 2 hours')
                    if hours > 2:
                        raise ValidationError('Short leave can apply only for 2 hours')

                if self.date_from and self.date_to:
                    if self.date_from > self.date_to:
                        raise ValidationError('From Date must be less than To Date')
                    duration = (self.date_to - self.date_from)
                    self.duration = duration.days + 1
                    if self.sub_leave_type == 'short' and self.date_from:
                        self.date_to = self.date_from
                        self.duration = 0.25
                    elif self.sub_leave_type == 'half' and self.date_from:
                        self.date_to = self.date_from
                        self.duration = 0.5
                    else:
                        duration = (self.date_to - self.date_from)
                        self.duration = duration.days + 1
                    if self.leave_type.name == 'Short Leave':
                        self.sub_leave_type = 'short'
                        self.duration = 1.0
                    if self.leave_type.name == 'Half Leave':
                        self.sub_leave_type = 'half'
                        self.duration = 1.0
                if self.leave_type.name in ('Casual Leaves', 'Annual Leaves'):
                    if self.date_from < datetime.date.today():
                        raise ValidationError('You can only apply for Pre leave')
                    if self.date_from <= datetime.date.today() and self.leave_type.name == 'Annual Leaves':
                        raise ValidationError('You can only apply for Pre leaves')
                    employees = self.env['hr.leave.employee'].search([('employee_id', '=', self.employee_id.ids[0]),
                                                                      ('id', '!=', self.ids[0]),
                                                                      ('leave_type', '=', self.leave_type.id),
                                                                      ('state', 'in', ('Approved',
                                                                                       'Manager Approval', 'Draft',
                                                                                       'HR Approval',
                                                                                       'COO Approval')),
                                                                      ('date_from', '>=',
                                                                       self.date_from.replace(day=1))])
                    duration = self.duration
                    for employee in employees:
                        duration += employee.duration
                    if self.leave_type.name == 'Casual Leaves' and duration > 2:
                        raise ValidationError('You cannot apply more than 2 Casual Leaves')
                    if self.leave_type.name == 'Annual Leaves' and self.duration < 7:
                        raise ValidationError('You cannot apply less than 7 Annual Leaves')
                    if self.leave_type.name == 'Annual Leaves' and self.date_from:
                        difference = self.date_from - datetime.date.today()
                        if difference.days < 15:
                            raise ValidationError('You have to apply Annual Leaves before 15 days')
                self.department_id = self.employee_id.department_id.id
                query = """
                select leave.name, sum(report.number_of_days), case when leave.leave_type_days = 'monthly'
                then leave.days_monthly_leave else leave.days_annual_leave end, leave.id, leave.no_of_year from hr_leave_report as report 
                INNER JOIN hr_leave_type as leave ON leave.id = report.holiday_status_id 
                where report.state = 'validate' and employee_id={} group by leave.name, leave.id;
                """.format(str(self.employee_id.ids[0]))

                self.env.cr.execute(query)
                employee_ids = self.env.cr.fetchall()
                lines = [(5, 0, 0)]

                for employee in employee_ids:
                    if employee[1] >= 0:
                        vals = {
                            'name': employee[0],
                            'available': employee[1],
                            'allocated': employee[2] * employee[4] if employee[2] is not None else employee[1],
                            'leave_type': employee[3],
                        }
                        lines.append((0, 0, vals))
                self.total_leave_summary = lines
                self.department_id = self.employee_id.department_id.id
                self.leave_report = self.env['hr.leave'].search(
                    [('employee_id', '=', self.employee_id.id), ('state', '=', 'validate')])
            self._onchange_allocated_leaves_check()
            MailTemplate = self.env.ref('update_timeoff_module_baykee.employee_manager_leave_approval_hr', False)
            if self.employee_id.work_email:
                email = self.employee_id.work_email
            else:
                email = 'sys@kknetworks.com.pk'
            if self.employee_id.ids[0] == self.department_id.manager_id.ids[0]:
                email_to = self.employee_id.parent_id.work_email
            else:
                email_to = self.department_id.manager_id.work_email
            MailTemplate.sudo().write({'email_from': email, 'email_to': email_to})
            MailTemplate.sudo().send_mail(self.ids[0], force_send=True)
            self.state = 'Manager Approval'


class EachEmployeeLeaveStatusForm(models.Model):
    _name = 'hr.leave.employee.report'
    _description = 'KKN HR Leave Employee Report'

    employee_leave = fields.Many2one('hr.leave.employee')
    name = fields.Char('Leave Type')
    available = fields.Char('Available Leaves')
    allocated = fields.Char('Allocated Leaves')
    leave_type = fields.Many2one('hr.leave.type', required=0, string="Leave Type")


class hr_approved_roster(models.TransientModel):
    _name = 'hr.approved.leave'
    _description = 'hr.approved.leave'

    def action_hr_approved_data(self):
        if self.env.user.has_group('update_timeoff_module_baykee.group_hr_right_leave') is False:
            raise ValidationError('Only HR Manager can approve this')
        leaves = self.env['hr.leave.employee'].search(
            [('id', 'in', self.env.context.get('active_ids')), ('state', '=', 'HR Approval')])
        if len(leaves) == 0:
            raise ValidationError('There is no entries in HR Approval stage')
        for ros in leaves:
            ros.state = 'COO Approval'


class coo_approved_roster(models.TransientModel):
    _name = 'coo.approved.leave'
    _description = 'coo.approved.leave'

    def action_coo_approved_data(self):
        if self.env.user.has_group('update_timeoff_module_baykee.group_coo_right_leave') is False:
            raise ValidationError('Only COO can approve this')
        leaves = self.env['hr.leave.employee'].search(
            [('id', 'in', self.env.context.get('active_ids')), ('state', '=', 'COO Approval')])
        if len(leaves) == 0:
            raise ValidationError('There is no entries in COO Approval stage')
        for ros in leaves:
            ros.request_approved()


class manager_approved_roster(models.TransientModel):
    _name = 'manager.approved.leave'
    _description = 'manager.approved.leave'

    def action_manager_approved_data(self):
        if self.env.user.has_group('update_timeoff_module_baykee.group_manager_right_leave') is False:
            raise ValidationError('Only Manager can approve this')
        leaves = self.env['hr.leave.employee'].search(
            [('id', 'in', self.env.context.get('active_ids')), ('state', '=', 'Manager Approval')])
        if len(leaves) == 0:
            raise ValidationError('There is no entries in Manager Approval stage')
        for ros in leaves:
            ros.request_complete()
