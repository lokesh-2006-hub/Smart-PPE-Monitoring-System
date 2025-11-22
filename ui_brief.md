# UI / Product Brief

**Project**: Smart PPE Compliance Monitoring — Web & Mobile Dashboard
**Audience**: Mine safety managers, gate operators, safety officers, admins
**Goal**: Provide real-time PPE compliance monitoring at mine entry gates with worker identification, auto alerts, historical reports, and trend analytics.
**Platform**: Responsive web dashboard (desktop first) + simple mobile view for on-the-go alerts.

## Pages / Components

### Login & Roles
- Login for Admin, Gate Operator, Safety Manager.
- Role-based UI.

### Gate Live View
- Real-time feed tile, currently tracked worker, small card showing:
    - Worker name & ID (or Unknown)
    - Photo thumbnail
    - PPE items status (helmet, cap lamp, boots, vest, gas detector, self-rescuer) — green ticks or red crosses
    - Compliance status (PASS/FAIL)
- Buttons: “Allow entry”, “Deny entry”, “Send SMS”, “Add note”
- History quick link for that worker

### People Directory
- Searchable list of known workers (photo, name, employee id, last seen, compliance rate).

### Events / Alerts
- Live alert list (non-compliance) with filter by severity/time/gate.

### Reports
- Daily / monthly compliance, top offenders, top performers, compliance trend chart, downloadable CSV.

### Settings / Hardware
- Configure gates, camera mapping, set TIME_WINDOW, CONF_THRESH, notification channels (SMS/email), offline sync settings.

### Offline / Sync Indicator
- Show whether edge device is online and when last sync happened.

## Design / UX

- **Minimal, high-contrast** for underground conditions. Use large readable fonts, color-coded statuses (green/yellow/red).
- Use a **card/grid approach** for the live feed area so multiple gates can be shown.
- Show big **PASS/FAIL badge** and the missing-PPE list for quick decisions.
- Add a small “Export” button on every report page.

## Tech Recommendation
- **Frontend**: React + Tailwind for web dashboard, React Native or PWA for mobile.
- **Backend**: FastAPI (Python) with SQLite/Postgres (or MySQL), WebSocket endpoint for push notifications.
