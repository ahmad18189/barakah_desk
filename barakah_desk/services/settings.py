import frappe

from barakah_desk.services.timezone import now_in_timezone, resolve_canonical_timezone


def get_settings_doc():
	return frappe.get_single("Barakah Desk Settings")


def get_effective_settings_payload():
	settings = get_settings_doc()
	timezone, timezone_source = resolve_canonical_timezone(settings)
	return {
		"enable_random_messages": settings.enable_random_messages,
		"enable_prayer_notifications": settings.enable_prayer_notifications,
		"message_schedule_mode": settings.message_schedule_mode,
		"message_interval_minutes": settings.message_interval_minutes,
		"show_arabic_messages": settings.show_arabic_messages,
		"show_english_messages": settings.show_english_messages,
		"prayer_notification_style": settings.prayer_notification_style,
		"city": settings.city,
		"country": settings.country,
		"timezone": timezone,
		"timezone_source": timezone_source,
		"server_now": now_in_timezone(timezone).isoformat(),
	}
