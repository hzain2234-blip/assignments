# Smart Bus — Hackathon Edition

A polished command-line bus ticket booking system built with Python and SQLite.

## Run in VS Code (Windows)

1. Extract this ZIP.
2. Open the extracted `Smart_Bus_Hackathon_Pro` folder in VS Code.
3. Open **Terminal → New Terminal**.
4. Run:

```powershell
python main.py
```

If `python` is not recognized, try `py main.py`.

No `requirements.txt` or pip installation is needed. The app uses Python's standard library only.

## Features

- Search routes by route ID or city
- View fares, schedule, and seat availability
- Book one or multiple seats with input validation and confirmation
- Unique booking IDs and booking lookup
- Cancel a booking once and automatically release seats
- Admin report with confirmed revenue and per-route performance
- SQLite database: bookings remain saved after closing the app
- Database constraints and parameterized SQL queries

## Files

- `main.py` — application
- `test_cases.txt` — manual testing checklist
- `smart_bus.db` — created automatically on first run

## Demo tip

For a quick live demo: view routes → search Hyderabad → book 2 seats on R101 → show availability → cancel the booking → open the report.

## Current scope / honest limitations

This is a local single-computer demo. It does not include online payments, real-time GPS, login/role authentication, or a shared server database. Do not describe those as implemented features during judging.
