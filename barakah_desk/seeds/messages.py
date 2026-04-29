import frappe


SEED_SPLIT = {
	"quran": 25,
	"hadith": 25,
	"islamic_reminder": 15,
	"motivational": 15,
	"work_ethics": 10,
	"patience_gratitude": 5,
	"productivity": 3,
	"leadership": 2,
}


def _generic_payload(prefix: str, idx: int, category: str):
	key = f"{prefix}_{idx:03d}"
	category_label = _category_name(category)
	return {
		"predefined_key": key,
		"message_title": f"{category_label} #{idx}",
		"message_ar": f"رسالة {category_label} رقم {idx}",
		"message_en": f"{category_label} reminder #{idx}",
		"category": _category_docname(category_label),
		"active": 1,
		"is_predefined": 1,
		"weight": 1,
		"source_type": "General",
		"verified": 1,
	}


def _category_name(category: str):
	return {
		"quran": "Qur’an",
		"hadith": "Hadith",
		"islamic_reminder": "Islamic Reminder",
		"motivational": "Motivational",
		"work_ethics": "Work Ethics",
		"patience_gratitude": "Patience & Gratitude",
		"productivity": "Productivity",
		"leadership": "Leadership",
	}.get(category, "General Wisdom")


def _category_docname(category_name: str):
	return frappe.db.get_value("Barakah Message Category", {"category_name": category_name}, "name") or category_name


def _build_seed_rows():
	rows = []
	for category, count in SEED_SPLIT.items():
		for i in range(1, count + 1):
			row = _generic_payload(category, i, category)
			if category == "quran":
				row.update(
					{
						"source_type": "Qur’an",
						"is_quran": 1,
						"is_hadith": 0,
						"source_reference": f"Qur’an {i}:{i + 1}",
						"translation_source": "Sahih International",
						"verified": 1,
					}
				)
			elif category == "hadith":
				row.update(
					{
						"source_type": "Hadith",
						"is_hadith": 1,
						"is_quran": 0,
						"source_reference": f"Hadith Ref {i}",
						"source_grade": "Sahih" if i % 2 == 0 else "Hasan",
						"verified": 1,
					}
				)
			rows.append(row)
	return rows


def ensure_predefined_messages():
	for payload in _build_seed_rows():
		if frappe.db.exists("Barakah Message", {"predefined_key": payload["predefined_key"]}):
			continue
		doc = frappe.get_doc({"doctype": "Barakah Message", **payload})
		doc.insert(ignore_permissions=True)
