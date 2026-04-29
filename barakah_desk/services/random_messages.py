import random

import frappe

from barakah_desk.services.settings import get_settings_doc


def _is_allowed(message, settings):
	if not message.active:
		return False
	if not settings.enable_predefined_messages and message.is_predefined:
		return False
	if not settings.enable_custom_messages and not message.is_predefined:
		return False
	if not settings.enable_quran_messages and message.is_quran:
		return False
	if not settings.enable_hadith_messages and message.is_hadith:
		return False
	if settings.hide_unverified_religious_messages and (message.is_quran or message.is_hadith) and not message.verified:
		return False
	if settings.show_arabic_messages and message.message_ar:
		return True
	if settings.show_english_messages and message.message_en:
		return True
	return False


def select_weighted_random_message():
	settings = get_settings_doc()
	messages = frappe.get_all("Barakah Message", fields=["name"])
	candidates = []
	weights = []
	for row in messages:
		doc = frappe.get_doc("Barakah Message", row.name)
		if not _is_allowed(doc, settings):
			continue
		candidates.append(doc)
		weights.append(max(1, int(doc.weight or 1)))
	if not candidates:
		return None
	return random.choices(candidates, weights=weights, k=1)[0]


def message_to_payload(message):
	return {
		"name": message.name,
		"title": message.message_title or "Barakah Reminder",
		"category": message.category,
		"message_ar": message.message_ar,
		"message_en": message.message_en,
		"source_type": message.source_type,
		"source_reference": message.source_reference,
		"translation_source": message.translation_source,
		"is_quran": bool(message.is_quran),
		"is_hadith": bool(message.is_hadith),
	}
