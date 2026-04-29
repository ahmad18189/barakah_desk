import frappe

from barakah_desk.services.random_messages import message_to_payload, select_weighted_random_message
from barakah_desk.services.settings import get_settings_doc


def _assert_system_manager():
	if "System Manager" not in frappe.get_roles():
		frappe.throw("Only System Manager can call this method")


@frappe.whitelist()
def get_random_message():
	if frappe.session.user == "Guest":
		return {"ok": False, "reason": "Authentication required"}
	message = select_weighted_random_message()
	if not message:
		return {"ok": False, "reason": "No eligible messages found"}
	return {"ok": True, "message": message_to_payload(message)}


@frappe.whitelist()
def preview_random_message():
	_assert_system_manager()
	return get_random_message()


@frappe.whitelist()
def trigger_random_message():
	_assert_system_manager()
	return get_random_message()


def _get_active_users():
	rows = frappe.db.sql(
		"""
		select distinct user
		from `tabSessions`
		where user != 'Guest'
		  and lastupdate >= (now() - interval 8 hour)
		""",
		as_dict=True,
	)
	return [row.user for row in rows if row.user]


def broadcast_random_message_to_active_users():
	message = select_weighted_random_message()
	if not message:
		return {"ok": False, "reason": "No eligible messages found", "sent_to_users": 0}

	payload = {"ok": True, "message": message_to_payload(message)}
	users = _get_active_users()
	for user in users:
		frappe.publish_realtime("barakah_random_message", payload, user=user)

	return {
		"ok": True,
		"message": payload["message"],
		"sent_to_users": len(users),
	}


@frappe.whitelist()
def trigger_random_message_broadcast():
	_assert_system_manager()
	return broadcast_random_message_to_active_users()


def trigger_random_message_from_scheduler():
	settings = get_settings_doc()
	if not settings.enable_random_messages:
		return {"ok": False, "reason": "Random messages disabled"}
	if settings.message_schedule_mode not in ("Interval", "Both"):
		return {"ok": False, "reason": "Interval mode disabled"}
	return broadcast_random_message_to_active_users()
