from odoo import http


class Appointment(http.Controller):
    @http.route("/today/appointment")
    def list(self):
        appointment = http.request.env["hospital.appointment"]
        appointments = appointment.search([])
        return http.request.render(
            "hospital_module.today_appointment_template",
            {"appointments": appointments}
        )

