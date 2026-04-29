import frappe

from barakah_desk.services.settings import get_effective_settings_payload


@frappe.whitelist()
def get_effective_notification_settings():
	if frappe.session.user == "Guest":
		frappe.throw("Authentication required")
	return {"ok": True, "settings": get_effective_settings_payload()}
