import frappe
from frappe.model.document import Document


class BarakahDeskSettings(Document):
	def validate(self):
		if not self.show_arabic_messages and not self.show_english_messages:
			frappe.throw("At least one language must be enabled.")

		if self.message_schedule_mode in ("Interval", "Both") and (self.message_interval_minutes or 0) <= 0:
			frappe.throw("Message interval minutes must be positive.")

		if self.enable_prayer_notifications:
			if not self.city or not self.country:
				frappe.throw("City and Country are required when prayer notifications are enabled.")
			if not any(row.enabled for row in self.enabled_prayer_events):
				frappe.throw("Enable at least one prayer event.")
			for row in self.enabled_prayer_events:
				alert_before = int(row.alert_before_minutes or 0)
				if alert_before < 0 or alert_before > 180:
					frappe.throw(f"Alert before minutes for {row.prayer_name or 'prayer'} must be between 0 and 180.")
