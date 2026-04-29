import frappe

from barakah_desk.services.prayer_times import compute_next_selected_event, get_today_prayer_times_payload


def _assert_system_manager():
	if "System Manager" not in frappe.get_roles():
		frappe.throw("Only System Manager can call this method")


@frappe.whitelist()
def get_next_prayer_event():
	if frappe.session.user == "Guest":
		return {"ok": False, "reason": "Authentication required"}
	return compute_next_selected_event()


@frappe.whitelist()
def preview_next_prayer_notification():
	_assert_system_manager()
	return compute_next_selected_event()


@frappe.whitelist()
def trigger_prayer_notification():
	_assert_system_manager()
	return compute_next_selected_event()


@frappe.whitelist()
def get_today_prayer_times():
	_assert_system_manager()
	return get_today_prayer_times_payload()
