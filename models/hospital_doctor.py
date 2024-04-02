from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HospitalDoctor(models.Model):
    _name = 'hospital.doctor'
    _description = 'Doctor Record'

    name = fields.Char(string='Name', required=True)
    phone = fields.Char(string="Phone", required=True)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string='Gender')
    age = fields.Integer(string='Age')
    section = fields.Many2one('doctor.section', string='Section', required=True)
    ticket_cost = fields.Integer(string='Ticket Cost')
    notes = fields.Text(string='Notes')
    date = fields.Date(string='Date')
    start_time = fields.Float(string='Start Time')
    end_time = fields.Float(string='End Time', readonly="True")
    slot_duration = fields.Float(string="Slot Duration")
    slot_count = fields.Integer(string="Slot Count")
    appointment_ids = fields.One2many('hospital.appointment.slot', 'doctor_id', string='Appointments')

    _sql_constraints = [
        ('unique_phone', 'UNIQUE(phone)', 'Phone number is exist')
    ]

    @api.constrains('phone')
    def _check_unique_phone(self):
        for rec in self:
            if rec.phone:
                existing_record = self.env['hospital.doctor'].search([('phone', '=', rec.phone), ('id', '!=', rec.id)],
                                                                     limit=1)
                if existing_record:
                    raise ValidationError("Phone number is exist")

    def create_appointment_slots(self):
        for doctor in self:
            end_time = doctor.start_time + doctor.slot_duration
            existing_slots = self.env['hospital.appointment.slot'].search([
                ('doctor_id', '=', doctor.id),
                ('date', '=', doctor.date),
                ('start_time', '=', doctor.start_time)
            ])
            if existing_slots:
                message = "Appointment slots already exist for the selected date and time."
                message_id = self.env['message.wizard'].create({'message': message})
                return {
                    'name': 'Error',
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'message.wizard',
                    'res_id': message_id.id,
                    'target': 'new'
                }
            else:
                for i in range(doctor.slot_count):
                    self.env['hospital.appointment.slot'].create({
                        'name': f"Dr.({self.name})-Date:({self.date})-Time:({self.start_time})",
                        'doctor_id': doctor.id,
                        'date': doctor.date,
                        'start_time': doctor.start_time,
                        'end_time': end_time,
                    })
                    doctor.start_time = end_time
                    end_time += doctor.slot_duration
        message_id = self.env['message.wizard'].create(
            {'message': "New slots have been created successfully."})
        return {
            'name': 'Success',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'message.wizard',
            'res_id': message_id.id,
            'target': 'new'
        }

    def clear_field(self):
        self.date = False
        self.start_time = False
        self.end_time = False
        self.slot_count = False
        self.slot_duration = False
        message_id = self.env['message.wizard'].create({'message': "Data are successfully cleared."})
        return {
            'name': 'Successful',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'message.wizard',
            'res_id': message_id.id,
            'target': 'new'
        }

    def action_add_appointment_slots(self):
        view_id = self.env.ref('hospital_module.view_hospital_doctor_add_slots').id
        return {
            'name': 'Add Appointment Slots',
            'view_mode': 'form',
            'res_model': 'hospital.doctor',
            'view_id': view_id,
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'create': True},
        }

    def action_add_appointments(self):
        for rec in self:
            search = self.env['hospital.doctor'].search([('name', '=', rec.name)], limit=1)
            if search:
                values = {
                    'doctor_id': search.id,
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

    def action_view_appointments(self):
        self.ensure_one()
        return {
            'name': 'Appointments',
            'view_mode': 'tree,form',
            'res_model': 'hospital.appointment',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('doctor_id', '=', self.id)],
            'target': 'new',
            'context': "{'create':False}",
        }

    def print_doctor(self):
        return self.env.ref('hospital_module.report_action_hospital_doctor').report_action(self)


class DoctorSection(models.Model):
    _name = 'doctor.section'
    _description = 'Doctor Section'

    name = fields.Char(string='Section', required=True)
    description = fields.Text(string='Description')
