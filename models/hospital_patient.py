from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HospitalPatient(models.Model):
    _name = 'hospital.patient'
    _description = 'Patient Record'

    name = fields.Char(string='Name', required=True)
    phone = fields.Char(string="Phone", required=True)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string='Gender')
    age = fields.Integer(string='Age')
    address = fields.Char(string='Address')
    Area = fields.Char(string='Area')
    blood_type = fields.Selection([('A', 'A'), ('B', 'B'), ('AB', 'AB'), ('O', 'O')], string="Blood Type")
    diseases = fields.Text(string='Diseases')
    medicines = fields.Text(string='Medicines')
    notes = fields.Text(string='Notes')
    total_patients = fields.Integer(string='Total Patients', compute='_compute_total_patients')
    appointment_ids = fields.One2many('hospital.appointment', 'patient_id', string='Appointments')

    _sql_constraints = [
        ('unique_phone', 'UNIQUE(phone)', 'Phone number is exist')
    ]

    @api.constrains('phone')
    def _check_unique_phone(self):
        # Loop through all records
        for rec in self:
            if rec.phone:
                existing_record = self.env['hospital.patient'].search([('phone', '=', rec.phone), ('id', '!=', rec.id)],
                                                                      limit=1)
                if existing_record:
                    raise ValidationError("Phone number is exist")

    def action_view_appointments(self):
        self.ensure_one()
        return {
            'name': 'Appointments',
            'view_mode': 'tree,form',
            'res_model': 'hospital.appointment',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('patient_id', '=', self.id)],
            'target': 'new',
            'context': "{'create':False}",
        }

    def action_add_appointments(self):
        for rec in self:
            search = self.env['hospital.patient'].search([('name', '=', rec.name)], limit=1)
            if search:
                values = {
                    'patient_id': search.id,
                }
                return {
                    'name': 'Add Appointment',
                    'view_mode': 'form',
                    'res_model': 'hospital.appointment',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                    'context': {'default_' + key: value for key, value in values.items()},
                }

    def print_patients(self):
        return self.env.ref('hospital_module.report_action_hospital_patient').report_action(self)
