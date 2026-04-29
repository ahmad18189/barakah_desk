import frappe


ITEM_LABEL = "Show Today Prayer Times"
ITEM_ACTION = "frappe.ui.toolbar.show_today_prayer_times()"


def ensure_prayer_times_navbar_item():
	settings = frappe.get_single("Navbar Settings")

	existing = None
	for row in settings.help_dropdown:
		if row.item_label == ITEM_LABEL or row.action == ITEM_ACTION:
			existing = row
			break

	if existing:
		existing.item_label = ITEM_LABEL
		existing.item_type = "Action"
		existing.action = ITEM_ACTION
		existing.route = None
		existing.hidden = 0
		existing.condition = "1"
		_move_after_about(settings, existing)
		settings.save(ignore_permissions=True)
		return

	settings.append(
		"help_dropdown",
		{
			"item_label": ITEM_LABEL,
			"item_type": "Action",
			"action": ITEM_ACTION,
			"condition": "1",
			"hidden": 0,
			"is_standard": 0,
		},
	)
	new_row = settings.help_dropdown.pop()
	_move_after_about(settings, new_row)

	settings.save(ignore_permissions=True)


def _move_after_about(settings, target_row):
	settings.help_dropdown = [row for row in settings.help_dropdown if row is not target_row]
	insert_at = len(settings.help_dropdown)
	for idx, row in enumerate(settings.help_dropdown):
		if row.item_label == "About" or row.action == "frappe.ui.toolbar.show_about()":
			insert_at = idx + 1
			break
	settings.help_dropdown.insert(insert_at, target_row)
	for idx, row in enumerate(settings.help_dropdown, start=1):
		row.idx = idx
