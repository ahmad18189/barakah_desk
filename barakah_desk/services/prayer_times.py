from datetime import datetime, timedelta
import frappe
import requests

from barakah_desk.services.settings import get_settings_doc
from barakah_desk.services.timezone import now_in_timezone, resolve_canonical_timezone

PRAYER_ORDER = ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]


def _request_prayer_timings(settings, date_str, timezone):
	cache_key = (
		f"prayer_times:muslimsalat:{date_str}:{settings.city}:{settings.country}:"
		f"{settings.prayer_calculation_method}:{timezone}"
	)
	cached = frappe.cache().get_value(cache_key)
	if cached:
		return cached

	url = f"https://muslimsalat.com/{settings.city}/daily.json"
	params = {
		"date": date_str,
		"country": settings.country,
		"key": "API_KEY",
		"method": settings.prayer_calculation_method or 2,
	}
	try:
		response = requests.get(url, params=params, timeout=10)
		response.raise_for_status()
		payload = response.json()
		if not payload or payload.get("status_code") != 1:
			raise ValueError("Invalid prayer API response")
		data = payload
		frappe.cache().set_value(cache_key, data, expires_in_sec=3600)
		return data
	except Exception:
		frappe.log_error(frappe.get_traceback(), "Barakah Prayer API Error")
		return None


def fetch_prayer_times():
	settings = get_settings_doc()
	if not settings.city or not settings.country:
		return None, "Prayer city/country is not configured"
	timezone, timezone_source = resolve_canonical_timezone(settings)
	now = now_in_timezone(timezone)
	date_str = now.strftime("%Y-%m-%d")
	data = _request_prayer_timings(settings, date_str, timezone)
	if not data:
		return None, "Prayer API unavailable"
	return {"data": data, "timezone": timezone, "timezone_source": timezone_source, "now": now}, None


def _parse_muslimsalat_time(time_str: str, base_date):
	parsed = datetime.strptime(time_str.strip().lower(), "%I:%M %p")
	return base_date.replace(hour=parsed.hour, minute=parsed.minute, second=0, microsecond=0)


def compute_next_selected_event():
	result, error = fetch_prayer_times()
	if error:
		return {"ok": False, "reason": error, "next_retry_seconds": 900}

	settings = get_settings_doc()
	items = result["data"].get("items", [])
	timings = items[0] if items else {}
	event_rows = {row.prayer_name: row for row in settings.enabled_prayer_events if row.enabled}
	now = result["now"]
	key_map = {
		"Fajr": "fajr",
		"Sunrise": "shurooq",
		"Dhuhr": "dhuhr",
		"Asr": "asr",
		"Maghrib": "maghrib",
		"Isha": "isha",
	}
	first_enabled_event = None
	first_enabled_prayer_dt = None
	for prayer_name in PRAYER_ORDER:
		row = event_rows.get(prayer_name)
		if not row:
			continue
		if first_enabled_event is None:
			first_enabled_event = prayer_name
		value = timings.get(key_map[prayer_name])
		if not value:
			continue
		prayer_dt = _parse_muslimsalat_time(value, now)
		if first_enabled_prayer_dt is None:
			first_enabled_prayer_dt = prayer_dt
		alert_before = int(row.alert_before_minutes or 0)
		alert_dt = prayer_dt - timedelta(minutes=alert_before)
		if alert_dt >= now:
			return {
				"ok": True,
				"timezone": result["timezone"],
				"timezone_source": result["timezone_source"],
				"server_now": now.isoformat(),
				"next_event": {
					"name": prayer_name,
					"prayer_time": prayer_dt.isoformat(),
					"alert_time": alert_dt.isoformat(),
					"alert_before_minutes": alert_before,
					"source": "MuslimSalat",
				},
			}

	if first_enabled_event and first_enabled_prayer_dt:
		first_row = event_rows.get(first_enabled_event)
		next_alert_before = int((first_row.alert_before_minutes if first_row else 0) or 0)
		next_day_prayer_dt = first_enabled_prayer_dt + timedelta(days=1)
		alert_dt = next_day_prayer_dt - timedelta(minutes=next_alert_before)
		return {
			"ok": True,
			"timezone": result["timezone"],
			"timezone_source": result["timezone_source"],
			"server_now": now.isoformat(),
			"next_event": {
				"name": first_enabled_event,
				"prayer_time": next_day_prayer_dt.isoformat(),
				"alert_time": alert_dt.isoformat(),
				"alert_before_minutes": next_alert_before,
				"source": "MuslimSalat",
			},
		}

	return {"ok": False, "reason": "No enabled prayer event found", "next_retry_seconds": 1800}


def get_today_prayer_times_payload():
	result, error = fetch_prayer_times()
	if error:
		return {"ok": False, "reason": error, "next_retry_seconds": 900}

	settings = get_settings_doc()
	items = result["data"].get("items", [])
	timings = items[0] if items else {}
	event_rows = {row.prayer_name: row for row in settings.enabled_prayer_events}
	key_map = {
		"Fajr": "fajr",
		"Sunrise": "shurooq",
		"Dhuhr": "dhuhr",
		"Asr": "asr",
		"Maghrib": "maghrib",
		"Isha": "isha",
	}

	events = []
	now = result["now"]
	for prayer_name in PRAYER_ORDER:
		value = timings.get(key_map[prayer_name])
		if not value:
			continue
		prayer_dt = _parse_muslimsalat_time(value, now)
		row = event_rows.get(prayer_name)
		alert_before = int((row.alert_before_minutes if row else 0) or 0)
		events.append(
			{
				"name": prayer_name,
				"enabled": bool(row.enabled) if row else False,
				"prayer_time": prayer_dt.isoformat(),
				"alert_before_minutes": alert_before,
				"alert_time": (prayer_dt - timedelta(minutes=alert_before)).isoformat(),
			}
		)

	return {
		"ok": True,
		"timezone": result["timezone"],
		"timezone_source": result["timezone_source"],
		"server_now": now.isoformat(),
		"source": "MuslimSalat",
		"events": events,
	}
