from odoo import api, models, fields


class MessageWizard(models.TransientModel):
    _name = 'message.wizard'
    message = fields.Text('Message', required=True, readonly=True)

    def action_ok(self):
        self.ensure_one()
        return {'type': 'ir.actions.act_window_close'}
