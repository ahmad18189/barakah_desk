import frappe


def test_barakah_settings_exists():
	doc = frappe.get_single("Barakah Desk Settings")
	assert doc.doctype == "Barakah Desk Settings"
