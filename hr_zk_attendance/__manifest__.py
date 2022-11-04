{
    'name': 'Biometric Device Integration PyZk',
    'version': '13.0.1',
    'summary': """Integrating Biometric Device With HR Attendance (Thumb)""",
    'description': """
        -  This module integrates Odoo with the biometric device. 
        -  When any employee check_in/out in device,
        -  After every 1 hour all records added in 2 databases (hr.attendance, zk.machine.attendance)
        -  You can download each machine attendance by clicking download attendance button
        -  You can test machine which is up or down by press connection test button

        -  In Employees there is one field name Barcode which linked with attendance user name
        -  Where button available generate employee code which automatically assign code to user.
        -  After assigning the code their is another button add that add new user in machine with integrated with machine.
        """,
    'category': 'Generic Modules/Human Resources',
    'author': 'Danish Khalid',
    'company': 'KK Networks',
    'website': "https://www.kknetworks.com.pk",
    'depends': ['base_setup', 'hr', 'hr_attendance'],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/zk_device_view.xml',
        'views/hr_employee.xml',
        'views/machine_analysis_view.xml',
        'views/employee_shift_view.xml',
        'views/hr_attendance_view.xml',
        'wizard/sh_message_wizard.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
