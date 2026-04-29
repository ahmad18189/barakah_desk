# Barakah Desk

**Prayer alerts and mindful reminders for Frappe Desk.**

Barakah Desk is a lightweight Frappe/ERPNext app that brings a calm Islamic rhythm into daily work. It shows Desk-wide motivational reminders, Islamic reminders, proverbs, and prayer time notifications directly inside the Frappe Desk, with Quran and Hadith content support ready for reviewed content packs.

> بَرَكَة في الوقت، وذكر في العمل، وتنبيه للصلاة داخل مكتبك اليومي.
>
> Barakah in time, remembrance in work, and prayer awareness inside your daily Desk.

## Why Barakah Desk?

Modern ERP systems help teams manage tasks, sales, finance, HR, inventory, and operations. Barakah Desk adds something different: a gentle reminder that work is also an amanah, time is a blessing, and prayer has priority.

It is built for Muslim-friendly workplaces, Islamic organizations, schools, charities, companies, and teams that want Frappe Desk to feel more aligned with their values.

## Installation

Barakah Desk is a Frappe app and should be installed using Bench.

### Requirements

- Frappe Framework v15
- ERPNext v15 compatible
- Python 3.10+
- A working Bench environment
- Outbound HTTPS access for prayer time API calls

### Get The App

From your bench directory:

```bash
cd /path/to/frappe-bench
bench get-app https://github.com/YOUR_ORG/barakah_desk.git
```

If you are installing from a specific branch:

```bash
cd /path/to/frappe-bench
bench get-app https://github.com/YOUR_ORG/barakah_desk.git --branch main
```

### Install On A Site

```bash
cd /path/to/frappe-bench
bench --site <site> install-app barakah_desk
bench --site <site> migrate
bench build --app barakah_desk
bench --site <site> clear-cache
bench restart
```

Example:

```bash
cd /path/to/frappe-bench
bench --site <site> install-app barakah_desk
bench --site <site> migrate
bench build --app barakah_desk
bench --site <site> clear-cache
bench restart
```

## Key Features

- Desk-wide reminders on Frappe pages after login.
- Random motivational, wisdom, productivity, leadership, work ethics, and Islamic reminder messages.
- Quran and Hadith message support is built in, with reviewed Quran/Hadith content packs planned as a TODO.
- Bilingual content support for Arabic and English.
- Predefined general reminder messages seeded on install.
- Custom messages managed from Frappe DocTypes.
- Category-based filtering.
- Quran and Hadith visibility controls.
- Verification controls for religious content.
- Interval-based message scheduling.
- Fixed daily message times.
- Prayer notifications based on configured city and country.
- Per-prayer alert lead time, for example 0, 5, 10, or 15 minutes before prayer.
- Select which prayer events are enabled: Fajr, Sunrise, Dhuhr, Asr, Maghrib, and Isha.
- Timezone-aware prayer display using Frappe System Settings.
- Today prayer times dialog from the Help menu.
- Live current time watch inside the prayer times dialog.
- Notification styles using `frappe.show_alert` or `frappe.msgprint`.
- Admin preview and trigger buttons.
- Arabic translations through `ar.csv`.
- Safe install seeding through `after_install`, without fixture dependency.

## Islamic Identity

Barakah Desk is designed around a simple idea: the workday should not make people forget prayer, gratitude, patience, sincerity, and excellence.

The app supports reminder categories for:

- Quran text and Quran reflections.
- Hadith text and Hadith reflections.
- Islamic reminders.
- Patience and gratitude messages.
- Work ethics reminders.
- General wisdom and proverbs.
- Productivity and leadership reminders.

Religious content can be controlled carefully. When Quran and Hadith messages are added, they should include source references, and settings allow administrators to hide unverified religious messages.

Current content note: reviewed Quran and Hadith messages are not preadded yet. Adding verified Quran and Hadith packs is tracked as a TODO.

## Prayer Times

Barakah Desk can notify users before or at selected prayer times.

Supported prayer events:

- Fajr
- Sunrise
- Dhuhr
- Asr
- Maghrib
- Isha

Prayer settings include:

- Enable or disable prayer notifications.
- City.
- Country.
- Prayer API provider.
- Prayer calculation method.
- Use Frappe System Settings timezone.
- Notification style.
- Enabled prayer events.
- Alert before minutes per prayer row.

The current implementation uses the `muslimsalat` provider directly because it was reachable and reliable from the tested server environment. Prayer times are cached server-side to avoid unnecessary API calls.

## Today Prayer Times Dialog

Barakah Desk adds a Help menu action:

`Help > Show Today Prayer Times`

This opens a clean dialog showing:

- Current time based on the configured Frappe timezone.
- Today's prayer names.
- Prayer times in `HH:MM AM/PM` format.
- Time remaining or passed status.

The same dialog can also be called from the browser console:

```javascript
frappe.ui.toolbar.show_today_prayer_times()
```

## Reminder Scheduling

Random reminders can be scheduled in three ways:

- `Interval`: show a random reminder every configured number of minutes.
- `Fixed Times`: show reminders at selected daily times.
- `Both`: combine interval and fixed daily reminders.

The frontend scheduler uses browser duplicate guards so users do not receive repeated prayer popups for the same event in the same browser session.

## Admin Controls

System Managers can open:

`Barakah Desk Settings`

From there, administrators can:

- Enable or disable random reminders.
- Enable or disable prayer notifications.
- Choose Arabic, English, or both.
- Enable or disable predefined messages.
- Enable or disable custom messages.
- Select message categories.
- Configure interval minutes.
- Configure fixed daily message times.
- Configure prayer location.
- Configure enabled prayer events.
- Configure alert lead time per prayer.
- Preview random messages.
- Trigger random notifications.
- Preview next prayer notification.
- Trigger prayer notification.
- Show today's prayer times.

## Post-Install Setup

After installation:

1. Log in as a System Manager.
2. Open `Barakah Desk Settings`.
3. Enable `Random Messages` if you want Desk reminders.
4. Enable `Prayer Notifications` if you want prayer alerts.
5. Set `City` and `Country`, for example `Riyadh` and `Saudi Arabia`.
6. Confirm `Use System Timezone` is enabled.
7. Go to `System Settings` and verify the timezone, for example `Asia/Riyadh`.
8. Select enabled prayer events.
9. Set `Alert Before Minutes` for each prayer row.
10. Save settings.
11. Use the preview and trigger buttons to test.

## Navbar Help Menu

On install, Barakah Desk programmatically adds this item to `Navbar Settings`:

- Item Label: `Show Today Prayer Times`
- Item Type: `Action`
- Action: `frappe.ui.toolbar.show_today_prayer_times()`

The item is inserted under `About` in the Help dropdown.

If you need to re-apply it manually:

```bash
cd /path/to/frappe-bench
bench --site <site> execute barakah_desk.seeds.navbar.ensure_prayer_times_navbar_item
bench --site <site> clear-cache
```

## Seeded Data

Barakah Desk uses an `after_install` script to create required default data.

The install script creates:

- Default message categories.
- Default Barakah Desk settings rows.
- Default prayer event rows.
- Predefined general reminder messages.
- Help dropdown action for today's prayer times.

The app does not rely on exported fixture JSON files for this seed data. The seed logic is idempotent, so it can safely add missing records without overwriting administrator edits.

Reviewed Quran and Hadith seed messages are intentionally not preadded yet. They should be added only after content review, source verification, and translation review.

## Main DocTypes

Barakah Desk includes these main DocTypes:

- `Barakah Desk Settings`: global app configuration.
- `Barakah Message Category`: reminder categories.
- `Barakah Message`: predefined and custom reminder content.
- `Barakah Fixed Message Time`: child table for fixed daily reminder times.
- `Barakah Enabled Message Category`: child table for enabled categories.
- `Barakah Prayer Event`: child table for selected prayer events and alert lead time.

## Backend API

The app exposes safe whitelisted methods for logged-in users and System Managers.

Settings:

- `barakah_desk.api.settings.get_effective_notification_settings`

Messages:

- `barakah_desk.api.messages.get_random_message`
- `barakah_desk.api.messages.preview_random_message`
- `barakah_desk.api.messages.trigger_random_message`

Prayer:

- `barakah_desk.api.prayer.get_next_prayer_event`
- `barakah_desk.api.prayer.preview_next_prayer_notification`
- `barakah_desk.api.prayer.trigger_prayer_notification`
- `barakah_desk.api.prayer.get_today_prayer_times`

## Frontend Integration

Barakah Desk loads a Desk-wide JavaScript file through Frappe hooks:

```python
app_include_js = ["/assets/barakah_desk/js/desk_notifications_0838.js"]
```

The JavaScript scheduler:

- Starts after Desk login.
- Fetches effective settings from the backend.
- Schedules random reminders.
- Schedules fixed-time reminders.
- Schedules prayer notifications.
- Registers `frappe.ui.toolbar.show_today_prayer_times()`.
- Uses local and session storage to reduce duplicate notifications.
- Handles API failures gracefully so Desk does not break.

## Permissions

- System Managers can configure settings and manage messages.
- Logged-in users can receive runtime notification payloads through whitelisted APIs.
- Guest users are not intended to access notification APIs.
- Religious content can be hidden unless verified.
- External API errors are handled gracefully and logged server-side.

## Timezone Behavior

Prayer notifications and today's prayer dialog are based on the canonical timezone resolved by the backend.

Priority:

1. Frappe `System Settings` timezone when `Use System Timezone` is enabled.
2. API/provider timezone if available.
3. UTC fallback.

For Saudi deployments, set:

`System Settings > Time Zone > Asia/Riyadh`

## Testing Prayer API Access

If prayer notifications do not appear, first confirm that your server can reach the provider over HTTPS.

Example:

```bash
curl -I https://muslimsalat.com
```

Then test from Frappe:

```bash
cd /path/to/frappe-bench
bench --site <site> execute barakah_desk.api.prayer.get_today_prayer_times
```

## Troubleshooting

If the Help menu item does not appear:

```bash
bench --site <site> execute barakah_desk.seeds.navbar.ensure_prayer_times_navbar_item
bench --site <site> clear-cache
bench restart
```

If the browser console says `frappe.ui.toolbar.show_today_prayer_times is not a function`:

```bash
bench build --app barakah_desk
bench --site <site> clear-cache
bench restart
```

Then hard refresh the browser.

If prayer times look wrong:

- Check `System Settings > Time Zone`.
- Enable `Use System Timezone` in `Barakah Desk Settings`.
- Confirm the city and country are correct.
- Clear cache and test again.

If the prayer API is unavailable:

- Confirm outbound port `443` is allowed.
- Test DNS and HTTPS from the server.
- Check Frappe error logs.
- Wait for the retry window, because API failures are cached briefly to avoid hammering the provider.

## Developer Notes

Useful commands:

```bash
cd /path/to/frappe-bench
bench --site <site> migrate
bench build --app barakah_desk
bench --site <site> clear-cache
bench restart
```

Run Python compile checks:

```bash
cd /path/to/frappe-bench/apps/barakah_desk
python3 -m compileall barakah_desk
```

Install pre-commit hooks:

```bash
cd /path/to/frappe-bench/apps/barakah_desk
pre-commit install
```

## Roadmap Ideas

- Multiple prayer API providers with admin fallback selection.
- Per-user city and country overrides.
- Per-user notification preferences.
- TODO: Add reviewed Quran content pack with verified Arabic text, source references, and approved translations.
- TODO: Add reviewed Hadith content pack with verified references, grades where applicable, and reviewed translations.
- Audio adhan option.
- Workspace widgets.
- Ramadan mode.
- Hijri date display.
- Organization-wide Islamic calendar reminders.

## App Information

- App Name: `Barakah Desk`
- Python Package: `barakah_desk`
- Framework: `Frappe Framework v15`
- ERPNext Compatibility: `ERPNext v15`
- License: `MIT`
- Tagline: `Prayer alerts and mindful reminders for Frappe Desk.`

## License

MIT
