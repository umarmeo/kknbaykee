import logging
from odoo import api, fields, models, _
from zk import ZK
from odoo.exceptions import UserError
log = logging.getLogger(__name__)



class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    device_id = fields.Char(string='Device ID', groups="hr.group_hr_user")
    
    def action_create_machine_users(self):
        new_wizard = self.env['azk.machine.user.create'].create({
            'employee_ids': self.ids,
        })
        return {
            'name': _('Create Machine User'),
            'view_mode': 'form',
            'res_model': 'azk.machine.user.create',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': new_wizard.id,
        }
    
    def action_delete_machine_users(self):
        self.ensure_one()
        if not self.device_id:
            raise UserError(_('Nothing to delete, Device ID not set.'))
        
        new_wizard = self.env['azk.machine.user.delete'].create({
            'employee_id': self.id,
        })
        return {
            'name': _('Delete Machine User'),
            'view_mode': 'form',
            'res_model': 'azk.machine.user.delete',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': new_wizard.id,
        }