from datetime import datetime
from zoneinfo import ZoneInfo

import frappe


def resolve_canonical_timezone(settings):
	if settings.use_system_timezone:
		system_timezone = frappe.db.get_single_value("System Settings", "time_zone")
		if system_timezone:
			return system_timezone, "system_settings"
	return "UTC", "utc_fallback"


def now_in_timezone(timezone: str):
	return datetime.now(ZoneInfo(timezone))
