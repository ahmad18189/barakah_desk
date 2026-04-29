import frappe


DEFAULT_PRAYER_EVENTS = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha", "Sunrise"]


def ensure_default_settings_rows():
	settings = frappe.get_single("Barakah Desk Settings")
	if not settings.enabled_message_categories:
		for row in frappe.get_all("Barakah Message Category", fields=["name"]):
			settings.append("enabled_message_categories", {"category": row.name, "enabled": 1})

	if not settings.enabled_prayer_events:
		for prayer_name in DEFAULT_PRAYER_EVENTS:
			settings.append(
				"enabled_prayer_events",
				{"prayer_name": prayer_name, "enabled": 0 if prayer_name == "Sunrise" else 1},
			)

	settings.save(ignore_permissions=True)
