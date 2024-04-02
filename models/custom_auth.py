from odoo import models, fields, api, exceptions


class CustomAuth(models.TransientModel):
    _name = 'custom.auth'

    password = fields.Char("Password", required=True)

    def authenticate(self):
        password = "1234"
        menu_id = 577
        if self.password == password:
            form_menu = self.env['ir.ui.menu'].search([('id', '=', menu_id)], limit=1)
            print(form_menu.name)
            return {
                'name': 'Add Appointment',
                'view_mode': 'form',
                'res_model': 'hospital.appointment',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'target': 'new',
            }

        else:
            raise exceptions.ValidationError("invalid password")
