import frappe
from frappe.model.document import Document


class BarakahMessage(Document):
	def validate(self):
		if not self.message_ar and not self.message_en:
			frappe.throw("At least one of Arabic/English message is required.")
		if int(self.weight or 1) < 1:
			frappe.throw("Weight must be 1 or greater.")
		if self.is_quran and self.is_hadith:
			frappe.throw("Message cannot be both Qur'an and Hadith.")
		if self.is_quran:
			if self.source_type != "Qur’an":
				frappe.throw("Qur'an messages must have source type Qur’an.")
			if not self.source_reference:
				frappe.throw("Qur'an source reference is required.")
			self.translation_source = self.translation_source or "Sahih International"
		if self.is_hadith:
			if self.source_type != "Hadith":
				frappe.throw("Hadith messages must have source type Hadith.")
			if not self.source_reference:
				frappe.throw("Hadith source reference is required.")
		if self.verified and not self.verified_on:
			self.verified_by = frappe.session.user
			self.verified_on = frappe.utils.now_datetime()
