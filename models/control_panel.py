from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ControlPanelQuery(models.TransientModel):
    _name = 'control.panel.query'
    _description = 'Control Panel for query'

    phone = fields.Char(string="Mobile")
    date = fields.Date(string="Date")
    section = fields.Many2one('doctor.section', string='Section')

    def search_for_patient(self):
        for rec in self:
            if rec.phone:
                search = self.env['hospital.patient'].search([('phone', '=', rec.phone)], limit=1)
                if search:
                    values = {
                        'name': search.name,
                        'age': search.age,
                        'phone': search.phone,
                        'diseases': search.diseases,
                        'notes': search.notes,
                    }
                    return {
                        'type': 'ir.actions.act_window',
                        'name': 'Requested INFO',
                        'view_mode': 'form',
                        'res_model': 'control.panel.results',
                        'target': 'new',
                        'context': {'default_' + key: value for key, value in values.items()},
                    }
                else:
                    if not search:
                        raise ValidationError("No Patients found for the provided phone number.")
            else:
                if not rec.phone:
                    raise ValidationError("No phone number provided.")

    def search_for_doctor(self):
        for rec in self:
            if rec.phone:
                search = self.env['hospital.doctor'].search([('phone', '=', rec.phone)], limit=1)
                if search:
                    values = {
                        'name': search.name,
                        'age': search.age,
                        'phone': search.phone,
                        'section': search.section.id,
                    }
                    return {
                        'type': 'ir.actions.act_window',
                        'name': 'Requested INFO',
                        'view_mode': 'form',
                        'res_model': 'control.panel.results',
                        'target': 'new',
                        'context': {'default_' + key: value for key, value in values.items()},
                    }
                else:
                    raise ValidationError("No Doctors found for the provided phone number.")
            else:
                if not rec.phone:
                    raise ValidationError("No phone number provided.")

    def search_for_section(self):
        for rec in self:
            if rec.section:
                search = self.env['hospital.doctor'].search([('section', '=', rec.section.id)], limit=1)
                if search:
                    return {
                        'type': 'ir.actions.act_window',
                        'name': 'Requested INFO',
                        'view_mode': 'tree',
                        'res_model': 'hospital.doctor',
                        'target': 'new',
                        'domain': [('section', '=', rec.section.id)],
                    }
                else:
                    raise ValidationError("No Sections found for the provided section.")
            else:
                raise ValidationError("No section provided.")

    def open_appointment_slot(self):
        for rec in self:
            if rec.date:
                search = self.env['hospital.appointment.slot'].search([('date', '=', rec.date)], limit=1)
                if search:
                    return {
                        'type': 'ir.actions.act_window',
                        'name': 'Requested INFO',
                        'view_mode': 'tree',
                        'res_model': 'hospital.appointment.slot',
                        'target': 'new',
                        'domain': [('date', '=', rec.date), ('is_booked', '=', False)],
                    }
                elif not search:
                    raise ValidationError("No slots found for the provided date.")
            else:
                raise ValidationError("No date provided.")

    def open_ticket_query(self):
        view_id = self.env.ref('hospital_module.ticket_query_view').id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Ticket Query',
            'view_mode': 'form',
            'res_model': 'ticket.query',
            'view_id': view_id,
            'target': 'new',
        }

    def close_window(self):
        self.ensure_one()
        return {'type': 'ir.actions.act_window_close'}


class ControlPanelResults(models.TransientModel):
    _name = 'control.panel.results'
    _description = 'Control Panel Results'

    phone = fields.Char(string="Mobile", readonly="True")
    name = fields.Char(string="Name", readonly="True")
    age = fields.Integer(string="Age", readonly="True")
    diseases = fields.Text(string='Diseases', readonly="True")
    notes = fields.Text(string='Notes', readonly="True")
    doctor_id = fields.Many2one('hospital.doctor', string='Doctor', readonly="True")
    section = fields.Many2one('doctor.section', string='Section', readonly="True")
    date = fields.Date(string="Date", readonly="True", help="Date of Appointment")
    start_time = fields.Float(string="Start Time", readonly="True")
    end_time = fields.Float(string="End Time", readonly="True")
    slot_id = fields.Many2one('hospital.appointment.slot', string='Slot', readonly="True")

    def open_appointment(self):
        for rec in self:
            search = self.env['hospital.patient'].search([('name', '=', rec.name)], limit=1)
            if search:
                values = {
                    'patient_id': search.id,
                }
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Appointments',
                    'view_mode': 'form',
                    'res_model': 'hospital.appointment',
                    'target': 'new',
                    'context': {'default_' + key: value for key, value in values.items()},
                }
