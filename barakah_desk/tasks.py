import frappe

from barakah_desk.api.messages import trigger_random_message_from_scheduler
from barakah_desk.services.settings import get_settings_doc


def _is_due_for_interval_dispatch():
	settings = get_settings_doc()
	interval_minutes = max(1, int(settings.message_interval_minutes or 60))

	cache = frappe.cache()
	cache_key = "barakah_desk:last_interval_random_dispatch_at"
	last_dispatch = cache.get_value(cache_key)
	now_dt = frappe.utils.now_datetime()

	if not last_dispatch:
		cache.set_value(cache_key, now_dt.isoformat())
		return True

	try:
		last_dt = frappe.utils.get_datetime(last_dispatch)
	except Exception:
		cache.set_value(cache_key, now_dt.isoformat())
		return True

	if (now_dt - last_dt).total_seconds() >= interval_minutes * 60:
		cache.set_value(cache_key, now_dt.isoformat())
		return True

	return False


def dispatch_interval_random_messages():
	settings = get_settings_doc()
	if not settings.enable_random_messages:
		return
	if settings.message_schedule_mode not in ("Interval", "Both"):
		return
	if not _is_due_for_interval_dispatch():
		return

	result = trigger_random_message_from_scheduler()
	frappe.logger("barakah_desk").info("Interval random dispatch: %s", result)
