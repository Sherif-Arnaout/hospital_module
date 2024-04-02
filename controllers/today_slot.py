from odoo import http


class Doctor(http.Controller):
    @http.route("/today/doctor")
    def list(self):
        doctor = http.request.env["hospital.appointment.slot"]
        doctors = doctor.search([])
        return http.request.render(
            "hospital_module.today_slot_template",
            {"doctors": doctors}
        )

