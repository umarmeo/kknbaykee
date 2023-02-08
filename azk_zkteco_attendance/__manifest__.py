# -*- coding: utf-8 -*-
{
    'name': 'ZKTeco Attendance machine integration',

    'version': '15.0.2',

    'summary': """Integrates Odoo attendance with ZKTeco attendance machines""",
    'description': """This module integrates Odoo attendance with ZKTeco attendance machines
     * This integration was tested with ZKTeco Biopro MV30. For other devices get in touch with us to give you a quick test
        * Integrates biometric device(Face+Thumb) with HR attendance. Tested with ZKTeco Biopro MV30
        * Managing attendance automatically
        * Keeps zk machine history in Odoo
        * Support multiple devices in different locations
        * Clear attendance history on machine from Odoo
    """,
    'category': 'Human Resources',
    'author': 'Azkatech',
    'company': 'Azkatech',
    'website': "https://azka.tech",
    'support': 'support+apps@azka.tech',
    'price': 80,
    'currency': 'USD',
    'depends': ['base_setup', 'hr_attendance', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/machine_view.xml',
        'views/machine_attendance_view.xml',
        'views/user_wizard_view.xml',
        'data/download_data.xml',

    ],
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
