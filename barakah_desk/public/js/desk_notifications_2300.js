(function () {
	if (typeof frappe === "undefined") return;

	const DAY_MS = 24 * 60 * 60 * 1000;

	const api = {
		settings: "barakah_desk.api.settings.get_effective_notification_settings",
		random: "barakah_desk.api.messages.get_random_message",
		nextPrayer: "barakah_desk.api.prayer.get_next_prayer_event",
		todayPrayers: "barakah_desk.api.prayer.get_today_prayer_times",
	};

	const call = (method) => frappe.call({ method }).then((r) => r.message || {});
	const hasDeskSession = () => Boolean(frappe.session?.user && frappe.session.user !== "Guest");

	const format12h = (isoValue) => {
		if (!isoValue) return "-";
		const dt = new Date(isoValue);
		if (Number.isNaN(dt.getTime())) return "-";
		return dt.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", hour12: true });
	};

	const formatTimeRemaining = (targetIso, baseIso) => {
		const target = new Date(targetIso).getTime();
		const base = new Date(baseIso || Date.now()).getTime();
		if (!target || !base || Number.isNaN(target) || Number.isNaN(base)) return "-";
		const diff = target - base;
		if (diff <= 0) return __("Passed");
		const totalMinutes = Math.ceil(diff / 60000);
		const hours = Math.floor(totalMinutes / 60);
		const minutes = totalMinutes % 60;
		if (hours <= 0) return `${minutes} ${__("min")}`;
		return `${hours}:${String(minutes).padStart(2, "0")} ${__("left")}`;
	};

	const renderRandom = (payload) => {
		const msg = payload?.message;
		if (!payload?.ok || !msg) return;
		const now = Date.now();
		if (window.__barakahDeskLastAlert?.name === msg.name && now - window.__barakahDeskLastAlert.at < 3000) return;
		window.__barakahDeskLastAlert = { name: msg.name, at: now };

		const parts = [`<b>${msg.title || __("Barakah Reminder")}</b>`];
		if (msg.message_ar) parts.push(msg.message_ar);
		if (msg.message_en) parts.push(msg.message_en);
		if (msg.source_reference) parts.push(msg.source_reference);
		frappe.show_alert({ message: __(parts.join("<br>")), indicator: "green" }, 5);
	};

	const renderPrayer = (payload, style) => {
		if (!payload?.ok || !payload.next_event) return;
		const event = payload.next_event;
		const message = `${event.name} at ${new Date(event.prayer_time).toLocaleTimeString()}`;
		if (style === "msgprint") {
			frappe.msgprint({ title: "Prayer Notification", message });
			return;
		}
		frappe.show_alert({ message, indicator: "green" }, 8);
	};

	const startIntervalRandomMessages = (minutes) => {
		const key = "barakah_desk_random_last_shown_at";
		const intervalMs = Math.max(1, parseInt(minutes || 60, 10)) * 60 * 1000;
		const tickMs = 15 * 1000;

		const tryShow = async () => {
			try {
				const payload = await call(api.random);
				renderRandom(payload);
				if (payload?.ok) {
					localStorage.setItem(key, new Date().toISOString());
				}
			} catch (e) {
			}
		};

		// Show once immediately after boot so users know interval mode is active.
		tryShow();

		setInterval(() => {
			const lastShown = localStorage.getItem(key);
			const lastTime = lastShown ? new Date(lastShown).getTime() : 0;
			const elapsed = Date.now() - lastTime;
			if (!lastTime || elapsed >= intervalMs) {
				tryShow();
			}
		}, tickMs);
	};

	const scheduleFixedTimes = (settings) => {
		const times = settings.fixed_message_times || [];
		times.forEach((row) => {
			if (!row.enabled || !row.time) return;
			const now = new Date();
			const [hour, minute] = row.time.split(":");
			const at = new Date(now);
			at.setHours(parseInt(hour, 10), parseInt(minute, 10), 0, 0);
			if (at <= now) at.setDate(at.getDate() + 1);
			setTimeout(async () => {
				const key = `barakah_desk_random_fixed_shown:${at.toISOString().slice(0, 10)}:${row.time}`;
				if (localStorage.getItem(key)) return;
				const payload = await call(api.random);
				renderRandom(payload);
				localStorage.setItem(key, "1");
				scheduleFixedTimes(settings);
			}, at.getTime() - now.getTime());
		});
	};

	const run = async () => {
		try {
			if (!hasDeskSession()) return;
			const settingsPayload = await call(api.settings);
			if (!settingsPayload?.ok) return;
			const settings = settingsPayload.settings || {};
			if (settings.enable_random_messages) {
				if (["Interval", "Both"].includes(settings.message_schedule_mode)) {
					startIntervalRandomMessages(settings.message_interval_minutes);
				}
				if (["Fixed Times", "Both"].includes(settings.message_schedule_mode)) {
					scheduleFixedTimes(settings);
					setInterval(() => {}, DAY_MS);
				}
			}

			if (settings.enable_prayer_notifications) {
				const schedulePrayer = async () => {
					const payload = await call(api.nextPrayer);
					if (!payload?.ok) {
						setTimeout(schedulePrayer, (payload?.next_retry_seconds || 900) * 1000);
						return;
					}
					const event = payload.next_event;
					const key = `barakah_desk_prayer_notified:${event.alert_time.slice(0, 10)}:${event.name}:${event.alert_before_minutes}:${settings.city}:${settings.country}`;
					const dueIn = Math.max(0, new Date(event.alert_time).getTime() - Date.now());
					setTimeout(async () => {
						if (!localStorage.getItem(key)) {
							renderPrayer(payload, settings.prayer_notification_style || "show_alert");
							localStorage.setItem(key, "1");
						}
						await schedulePrayer();
					}, dueIn);
				};
				await schedulePrayer();
			}
		} catch (e) {
		}
	};

	const wireRealtimeRandomMessages = () => {
		if (!frappe.realtime?.on) return;
		frappe.realtime.on("barakah_random_message", (payload) => {
			renderRandom(payload);
		});
	};

	frappe.ui = frappe.ui || {};
	frappe.ui.toolbar = frappe.ui.toolbar || {};
	frappe.ui.toolbar.show_today_prayer_times = function () {
		if (!hasDeskSession()) {
			frappe.msgprint({
				title: __("Today Prayer Times"),
				indicator: "orange",
				message: __("Please login to use this action."),
			});
			return false;
		}

		frappe.call({
			method: api.todayPrayers,
			callback(r) {
				const payload = r.message || {};
				if (!payload.ok) {
					frappe.msgprint({
						title: __("Today Prayer Times"),
						indicator: "orange",
						message: __(payload.reason || "Unable to fetch today prayer times."),
					});
					return;
				}
				const rows = (payload.events || [])
					.filter((evt) => evt.enabled)
					.map(
						(evt) => `
						<tr>
							<td>${__(evt.name || "-")}</td>
							<td>${format12h(evt.prayer_time)}</td>
							<td>${formatTimeRemaining(evt.prayer_time, payload.server_now)}</td>
						</tr>`
					);
				frappe.msgprint({
					title: __("Today Prayer Times"),
					indicator: "blue",
					message: `
						<table class="table table-bordered">
							<thead>
								<tr>
									<th>${__("Prayer")}</th>
									<th>${__("Prayer Time")}</th>
									<th>${__("Time Remaining")}</th>
								</tr>
							</thead>
							<tbody>${rows.join("")}</tbody>
						</table>`,
					wide: false,
				});
			},
			error(err) {
				frappe.msgprint({
					title: __("Today Prayer Times"),
					indicator: "red",
					message: __("Unable to fetch today prayer times."),
				});
			},
		});
		return false;
	};

	let schedulerStarted = false;
	const startSchedulerWhenSessionReady = (attempt = 0) => {
		if (schedulerStarted) return;
		if (!hasDeskSession()) {
			if (attempt >= 80) {
				return;
			}
			setTimeout(() => startSchedulerWhenSessionReady(attempt + 1), 250);
			return;
		}
		schedulerStarted = true;
		run();
	};

	if (window.__barakahDeskBooted) {
		return;
	}
	window.__barakahDeskBooted = true;
	wireRealtimeRandomMessages();

	startSchedulerWhenSessionReady();
	if (typeof frappe.ready === "function") {
		setTimeout(() => startSchedulerWhenSessionReady(), 0);
	} else if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", () => startSchedulerWhenSessionReady(), { once: true });
	} else {
		setTimeout(() => startSchedulerWhenSessionReady(), 0);
	}
})();
