import frappe


DEFAULT_CATEGORIES = [
	("Qur’an", 1),
	("Hadith", 1),
	("Islamic Reminder", 1),
	("Motivational", 1),
	("Work Ethics", 1),
	("Patience & Gratitude", 1),
	("Productivity", 1),
	("Leadership", 1),
	("General Wisdom", 1),
]


def ensure_default_categories():
	for index, (name, enabled) in enumerate(DEFAULT_CATEGORIES, start=1):
		if frappe.db.exists("Barakah Message Category", {"category_name": name}):
			continue
		doc = frappe.get_doc(
			{
				"doctype": "Barakah Message Category",
				"category_name": name,
				"enabled_by_default": enabled,
				"sort_order": index,
			}
		)
		doc.insert(ignore_permissions=True)
