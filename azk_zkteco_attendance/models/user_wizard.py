
import logging
from odoo import api, fields, models
from odoo.exceptions import UserError



log = logging.getLogger(__name__)

class CreateMachineUser(models.TransientModel):
    _name = 'azk.machine.user.create'
    _description = 'Create Machine User'
    
    employee_ids = fields.Many2many('hr.employee', string="employee")
    machine_id = fields.Many2one('azk.machine', string='Machine')
    link_if_exists = fields.Boolean(string='Link User If Exists', help="If employee name is found on machine, it will update User ID on employee card")

    def create_user(self):
        result = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Create status',
                'message': '',
                'sticky': True,
            }
        }
        conn = False
        errors = []
        created_count = 0
        try:
            conn, _ = self.machine_id.connect()
            if conn:
                for record in self.employee_ids: 
                    if record.device_id:
                        found_user = self.machine_id.check_user_id_availabilty(record.device_id, conn)
                        if found_user:
                            if found_user.name.lower() == record.name.lower():
                                errors.append("%s with device ID: %s already created." % (record.name, record.device_id))
                            else:
                                errors.append("Device ID: %s already bound to user %s." % ( record.device_id, record.name))
                        else:
                            try:
                                conn.set_user(name=record.name, user_id=record.device_id)
                                record.message_post(body="User {0} created on machine {0} with Device Id {2}".format(record.name, self.machine_id.name, record.device_id))
                                created_count +=1
                            except Exception as ex:
                                error = "Could not create employee {0} with deviceId: {1}. Exception occurred: {2}".format(record.name, record.device_id, ex.name)
                                log.info(error)
                                errors.append(error)
                                continue  
                    else:
                        try:
                            conn.get_users() # we have to call get_users() for next_user_id to work correctly
                               
                            device_id = conn.next_user_id
                            if self.link_if_exists:
                                user = self.machine_id.check_username_exists(record.name, conn)
                                if user:
                                    record.device_id = user.user_id
                                    msg = "User {0} is linked on machine {1} with Device Id {2}".format(record.name, self.machine_id.name, user.user_id)
                                    record.message_post(body=msg)
                                    errors.append(msg)
                            else:
                                conn.set_user(name=record.name, user_id=record.device_id)
                                record.device_id = device_id
                                msg = "User {0} is created on machine {1} with Device Id {2}".format(record.name, self.machine_id.name, device_id)
                                record.message_post(body=msg)
                                errors.append(msg)
                                created_count +=1
                        except Exception as ex:
                            error = "Could not create employees {0} . Exception occurred: {1}".format(record.name,  ex.name)
                            log.info(error)
                            errors.append(error)
                            continue  
                                   
        except Exception as e:
            raise UserError(e.name)
            result = {
                        'type': 'ir.actions.do_nothing'
                     }
        finally:
            if conn: conn.disconnect()
        
        errors.insert(0, "%s Employees has been created successfully.\n" % (created_count) )
        result['params']['message'] = "\n".join(errors)
        
        return result


class DeleteMachineUser(models.TransientModel):
    _name = 'azk.machine.user.delete'
    _description = 'Delete Machine User'
    
    employee_id = fields.Many2one('hr.employee', string="employee")
    machine_id = fields.Many2one('azk.machine', string='Machine')

    
    def delete_user(self):
        self.ensure_one()
        result = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Delete status',
                'message': 'User has been deleted successfully',
                'sticky': True,
            }
        }
        conn = False
         
        try:
            conn, _ = self.machine_id.connect()
 
            if conn:
                found_user = self.machine_id.check_user_id_availabilty(self.employee_id.device_id, conn)
                if not found_user:
                   raise UserError('User does not exist on machine')
                else:
                    res = conn.delete_user(user_id=self.employee_id.device_id)
                    self.employee_id.device_id = False
                    self.employee_id.message_post(body="User {0} is linked on machine {1} with Device Id {2}".format(self.employee_id.name, self.machine_id.name, self.employee_id.device_id))
        except Exception as ex:
            raise UserError(str(ex))
            result = {
                        'type': 'ir.actions.do_nothing'
                     }
        finally:
            if conn: conn.disconnect()
             
        return result