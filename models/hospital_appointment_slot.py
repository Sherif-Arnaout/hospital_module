from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HospitalAppointmentSlot(models.Model):
    _name = 'hospital.appointment.slot'
    _description = 'Appointment Slot'

    name = fields.Char(string='Appointment Slot', readonly="True")
    doctor_id = fields.Many2one('hospital.doctor', string='Doctor', readonly="True", required=True)
    section = fields.Many2one('doctor.section', string="Section")
    date = fields.Date(string='Date', readonly="True")
    start_time = fields.Float(string='Start Time', readonly="True")
    end_time = fields.Float(string='End Time', readonly="True")
    slot_duration = fields.Float(string="Slot Duration", readonly="True")
    slot_count = fields.Integer(string="Slot Count", readonly="True")
    is_booked = fields.Boolean(string='Is Booked', readonly="True", default=False)

    def create_appointment_slots(self):
        for doctor in self:
            end_time = doctor.start_time + doctor.slot_duration
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
                    {'message': "Appointment slots are successfully created."})
            return {
                    'name': 'Successful',
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

    def open_appointment(self):
        for rec in self:
            if not rec.is_booked:
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Appointments',
                    'view_mode': 'form',
                    'res_model': 'hospital.appointment',
                    'target': 'new',
                }
            else:
                raise ValidationError("The slot is already booked. Please choose another slot.")
