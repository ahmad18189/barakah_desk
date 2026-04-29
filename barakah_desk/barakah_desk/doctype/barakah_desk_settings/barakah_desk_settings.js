frappe.ui.form.on("Barakah Desk Settings", {
	refresh(frm) {
		toggle_fields(frm);
		add_buttons(frm);
		wire_random_message_alert_listener();
	},
	enable_random_messages(frm) {
		toggle_fields(frm);
	},
	enable_prayer_notifications(frm) {
		toggle_fields(frm);
	},
	message_schedule_mode(frm) {
		toggle_fields(frm);
	},
	validate(frm) {
		if (!frm.doc.show_arabic_messages && !frm.doc.show_english_messages) {
			frappe.throw(__("At least one language must be enabled."));
		}
	},
});

function toggle_fields(frm) {
	const randomVisible = !!frm.doc.enable_random_messages;
	const prayerVisible = !!frm.doc.enable_prayer_notifications;
	[
		"enable_predefined_messages",
		"enable_custom_messages",
		"show_arabic_messages",
		"show_english_messages",
		"enable_quran_messages",
		"enable_hadith_messages",
		"hide_unverified_religious_messages",
		"message_selection_mode",
		"enabled_message_categories",
		"message_schedule_mode",
	].forEach((f) => frm.toggle_display(f, randomVisible));

	frm.toggle_display("message_interval_minutes", randomVisible && ["Interval", "Both"].includes(frm.doc.message_schedule_mode));
	frm.toggle_display("fixed_message_times", randomVisible && ["Fixed Times", "Both"].includes(frm.doc.message_schedule_mode));
	["city", "country", "use_system_timezone", "prayer_api_provider", "prayer_calculation_method", "prayer_notification_style", "enabled_prayer_events"].forEach((f) =>
		frm.toggle_display(f, prayerVisible)
	);
}

function add_buttons(frm) {
	frm.add_custom_button(__("Preview Random Message"), async () => {
		const r = await frappe.call("barakah_desk.api.messages.preview_random_message");
		frappe.msgprint(`<pre>${JSON.stringify(r.message, null, 2)}</pre>`);
	}, __("Random Messages"));
	frm.add_custom_button(__("Trigger Random Notification"), async () => {
		const r = await frappe.call("barakah_desk.api.messages.trigger_random_message_broadcast");
		render_random_message_alert(r.message?.message);
	}, __("Random Messages"));
	frm.add_custom_button(__("Preview Next Prayer Notification"), async () => {
		const r = await frappe.call("barakah_desk.api.prayer.preview_next_prayer_notification");
		const payload = r.message || {};
		if (!payload.ok) {
			frappe.msgprint({
				title: __("Prayer Preview"),
				indicator: "orange",
				message: __(payload.reason || "Unable to fetch next prayer notification preview."),
			});
			return;
		}
		const event = payload.next_event || {};
		frappe.msgprint({
			title: __("Preview Next Prayer Notification"),
			indicator: "blue",
			message: prayer_notification_preview_html(event, payload),
		});
	}, __("Prayer"));
	frm.add_custom_button(__("Trigger Prayer Notification"), async () => {
		const r = await frappe.call("barakah_desk.api.prayer.trigger_prayer_notification");
		const payload = r.message || {};
		const event = payload.next_event;
		if (!event) return;
		if (frm.doc.prayer_notification_style === "msgprint") {
			frappe.msgprint({
				title: __("Prayer Notification"),
				indicator: "green",
				message: prayer_notification_preview_html(event, payload),
			});
		} else {
			frappe.show_alert({ message: `${event.name} at ${format_prayer_time(event.prayer_time)}`, indicator: "green" }, 8);
		}
	}, __("Prayer"));
	frm.add_custom_button(__("Show Today Prayer Times"), async () => {
		if (frappe.ui.toolbar?.show_today_prayer_times) {
			await frappe.ui.toolbar.show_today_prayer_times();
			return;
		}
		frappe.msgprint({
			title: __("Today Prayer Times"),
			indicator: "orange",
			message: __("Prayer time dialog is not ready yet. Please refresh the page."),
		});
	}, __("Prayer"));
}

function format_prayer_time(iso_value) {
	if (!iso_value) return "-";
	const dt = new Date(iso_value);
	if (Number.isNaN(dt.getTime())) return "-";
	return dt.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", hour12: true });
}

function prayer_notification_preview_html(event, payload) {
	const rows = [
		[__("Prayer"), __(event.name || "-")],
		[__("Prayer Time"), format_prayer_time(event.prayer_time)],
		[__("Alert Time"), format_prayer_time(event.alert_time)],
		[__("Alert Before (minutes)"), event.alert_before_minutes ?? 0],
		[__("Timezone"), payload.timezone || "-"],
		[__("Source"), event.source || "-"],
	];
	return `
		<table class="table table-bordered" style="margin-bottom: 0;">
			<tbody>
				${rows
					.map(
						([label, value]) => `
							<tr>
								<td style="width: 45%; color: var(--text-muted);">${label}</td>
								<td><b>${value}</b></td>
							</tr>`
					)
					.join("")}
			</tbody>
		</table>`;
}

function render_random_message_alert(message) {
	if (!message) return;
	const now = Date.now();
	if (window.__barakahDeskLastAlert?.name === message.name && now - window.__barakahDeskLastAlert.at < 3000) return;
	window.__barakahDeskLastAlert = { name: message.name, at: now };

	frappe.show_alert(
		{
			message: __([`<b>${message.title || __("Barakah Reminder")}</b>`, message.message_ar, message.message_en, message.source_reference].filter(Boolean).join("<br>")),
			indicator: "green",
		},
		5
	);
}

function wire_random_message_alert_listener() {
	if (window.__barakahDeskSettingsRealtimeAlertListener) return;
	if (!frappe.realtime?.on) return;

	window.__barakahDeskSettingsRealtimeAlertListener = true;
	frappe.realtime.on("barakah_random_message", (payload) => {
		render_random_message_alert(payload?.message);
	});
}
