import frappe


def execute():
	settings = frappe.get_single("Barakah Desk Settings")
	legacy_value = int(getattr(settings, "alert_before_minutes", 0) or 0)
	updated = False
	for row in settings.enabled_prayer_events:
		if row.alert_before_minutes is None:
			row.alert_before_minutes = legacy_value
			updated = True
	if updated:
		settings.save(ignore_permissions=True)
