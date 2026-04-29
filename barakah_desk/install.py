import frappe

from barakah_desk.seeds.categories import ensure_default_categories
from barakah_desk.seeds.default_settings import ensure_default_settings_rows
from barakah_desk.seeds.messages import ensure_predefined_messages
from barakah_desk.seeds.navbar import ensure_prayer_times_navbar_item


def after_install():
	bootstrap_defaults()


def bootstrap_defaults():
	ensure_default_categories()
	ensure_default_settings_rows()
	ensure_predefined_messages()
	ensure_prayer_times_navbar_item()
	frappe.db.commit()
