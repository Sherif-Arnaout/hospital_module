from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HospitalAppointment(models.Model):
    _name = 'hospital.appointment'
    _description = 'Appointment'

    doctor_id = fields.Many2one('hospital.doctor', string='Doctor', required=True, store=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True, store=True)
    phone = fields.Char(string="Patient Phone", related="patient_id.phone")
    slot_id = fields.Many2one('hospital.appointment.slot', string='Appointment Slot', required=True)
    date = fields.Date(related='slot_id.date', string='Date', store=True)
    start_time = fields.Float(related='slot_id.start_time', string='Start Time', store=True)
    end_time = fields.Float(related='slot_id.end_time', string='End Time', store=True)
    state_id = fields.Selection(
        [('new', 'New'),
         ('booked', 'Booked'),
         ('canceled', 'Canceled'), ],
        string='State', default="new")
    section = fields.Many2one('doctor.section', string='Section', related='doctor_id.section')
    ticket_cost = fields.Integer(string='Ticket Cost', related='doctor_id.ticket_cost')
    doctor_ticket_cost = fields.Integer(string='All Doctor Ticket Cost', compute='_compute_doctor_ticket_cost')
    start_date_period = fields.Date(string='Start Date Period')
    end_date_period = fields.Date(string='End Date Period')
    doctor_ticket_cost_period = fields.Integer(string='Doctor Ticket Cost (Period)',
                                               compute='_compute_doctor_ticket_cost_period')

    @api.depends('slot_id.doctor_id', 'ticket_cost')
    def _compute_doctor_ticket_cost(self):
        for appointment in self:
            doctor_id = appointment.slot_id.doctor_id
            appointments_with_same_doctor = self.env['hospital.appointment'].search([
                ('slot_id.doctor_id', '=', doctor_id.id),
                ('state_id', '=', 'booked'),  # Filter only booked appointments
            ])
            total_ticket_cost = sum(app.ticket_cost for app in appointments_with_same_doctor)
            appointment.doctor_ticket_cost = total_ticket_cost

    @api.depends('slot_id.doctor_id', 'ticket_cost', 'start_date_period', 'end_date_period')
    def _compute_doctor_ticket_cost_period(self):
        for appointment in self:
            doctor_id = appointment.slot_id.doctor_id
            appointments_with_same_doctor = self.env['hospital.appointment'].search([
                ('slot_id.doctor_id', '=', doctor_id.id),
                ('state_id', '=', 'booked'),  # Filter only booked appointments
                ('date', '>=', appointment.start_date_period),
                ('date', '<=', appointment.end_date_period),
            ])
            total_ticket_cost = sum(app.ticket_cost for app in appointments_with_same_doctor)
            appointment.doctor_ticket_cost_period = total_ticket_cost

    def confirm_booking(self):
        if self.state_id == "new" and not self.slot_id.is_booked:
            self.slot_id.is_booked = True
            self.state_id = "booked"
            message_id = self.env['message.wizard'].create({'message': "Booking is successfully confirmed."})
            return {
                'name': 'Successful',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'message.wizard',
                'res_id': message_id.id,
                'target': 'new'
            }
        elif self.state_id == "new" and self.slot_id.is_booked:
            raise ValidationError("Can't book! Appointment is already booked, please choose another slot.")
        elif self.state_id == "booked":
            raise ValidationError("Can't book! Appointment is already booked.")
        elif self.state_id == "canceled":
            raise ValidationError("Can't book! The booking was canceled before.")

    def cancel_booking(self):
        self.slot_id.is_booked = False
        self.state_id = "canceled"
        message_id = self.env['message.wizard'].create({'message': "Booking is successfully canceled."})
        return {
            'name': 'Successful',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'message.wizard',
            'res_id': message_id.id,
            'target': 'new'
        }

    def print_appointment(self):
        return self.env.ref('hospital_module.report_action_hospital_appointment').report_action(self)
