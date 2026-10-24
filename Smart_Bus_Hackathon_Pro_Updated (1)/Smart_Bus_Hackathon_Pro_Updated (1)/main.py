"""
SMART BUS — Hackathon Edition
Python 3.9+ | Standard library only | SQLite persistence
Run: python main.py
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).with_name("smart_bus.db")
CITIES = ("Karachi", "Hyderabad", "Sukkur", "Mirpur Khas", "Lahore")

SEED_ROUTES = (
    ("R101", "Karachi", "Hyderabad", "08:00 AM", 1200, 40),
    ("R102", "Karachi", "Sukkur", "09:30 AM", 2000, 36),
    ("R103", "Hyderabad", "Mirpur Khas", "11:00 AM", 800, 32),
    ("R104", "Karachi", "Lahore", "07:00 PM", 5000, 45),
    ("R105", "Sukkur", "Hyderabad", "02:00 PM", 1500, 30),
    ("R106", "Mirpur Khas", "Hyderabad", "09:00 AM", 800, 30),
    ("R107", "Mirpur Khas", "Karachi", "10:00 AM", 1500, 35),
    ("R108", "Lahore", "Karachi", "08:00 PM", 5000, 45),
    ("R109", "Lahore", "Hyderabad", "06:00 PM", 4500, 40),
)


def money(amount: int) -> str:
    return f"Rs. {amount:,.0f}"


def line(char="─", width=76):
    print(char * width)


def heading(title: str):
    print()
    line("═")
    print(f"  {title}")
    line("═")


def connect():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    with connect() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS routes (
                route_id TEXT PRIMARY KEY,
                departure_city TEXT NOT NULL,
                destination_city TEXT NOT NULL,
                departure_time TEXT NOT NULL,
                ticket_price INTEGER NOT NULL CHECK(ticket_price >= 0),
                total_seats INTEGER NOT NULL CHECK(total_seats > 0)
            );

            CREATE TABLE IF NOT EXISTS bookings (
                booking_id TEXT PRIMARY KEY,
                passenger_name TEXT NOT NULL,
                passenger_age INTEGER NOT NULL CHECK(passenger_age > 0),
                route_id TEXT NOT NULL REFERENCES routes(route_id),
                seats INTEGER NOT NULL CHECK(seats > 0),
                total_fare INTEGER NOT NULL CHECK(total_fare >= 0),
                status TEXT NOT NULL CHECK(status IN ('Confirmed', 'Cancelled')),
                created_at TEXT NOT NULL
            );
        """)
        # Seed any missing routes on every startup. Existing routes and bookings
        # are preserved because INSERT OR IGNORE skips route IDs already present.
        db.executemany(
            """INSERT OR IGNORE INTO routes
               (route_id, departure_city, destination_city, departure_time,
                ticket_price, total_seats)
               VALUES (?, ?, ?, ?, ?, ?)""",
            SEED_ROUTES,
        )


def route_available_seats(db, route_id):
    route = db.execute("SELECT total_seats FROM routes WHERE route_id = ?", (route_id,)).fetchone()
    if not route:
        return 0
    booked = db.execute(
        "SELECT COALESCE(SUM(seats), 0) FROM bookings WHERE route_id = ? AND status = 'Confirmed'",
        (route_id,),
    ).fetchone()[0]
    return route["total_seats"] - booked


def get_route(db, route_id):
    return db.execute("SELECT * FROM routes WHERE UPPER(route_id) = UPPER(?)", (route_id.strip(),)).fetchone()


def all_routes(db):
    rows = db.execute("SELECT * FROM routes ORDER BY route_id").fetchall()
    return [(r, route_available_seats(db, r["route_id"])) for r in rows]


def print_routes(db, available_only=False, rows=None):
    heading("BUS ROUTES & FARES")
    print(f"{'ID':<7} {'JOURNEY':<34} {'DEPARTURE':<13} {'FARE':>12} {'SEATS':>12}  STATUS")
    line()
    count = 0
    items = rows if rows is not None else all_routes(db)
    for route, available in items:
        if available_only and available <= 0:
            continue
        count += 1
        journey = f'{route["departure_city"]} → {route["destination_city"]}'
        status = "FULL" if available == 0 else ("LIMITED" if available <= 5 else "AVAILABLE")
        seat_text = f'{available}/{route["total_seats"]}'
        print(f'{route["route_id"]:<7} {journey:<34} {route["departure_time"]:<13} '
              f'{money(route["ticket_price"]):>12} {seat_text:>12}  {status}')
    if count == 0:
        print("No routes found.")
    line()


def prompt_nonempty(message, max_length=80):
    while True:
        value = input(message).strip()
        if value and len(value) <= max_length:
            return value
        print(f"Please enter a value (1–{max_length} characters).")


def prompt_int(message, minimum=1, maximum=None):
    while True:
        raw = input(message).strip()
        try:
            value = int(raw)
        except ValueError:
            print("Please enter a whole number.")
            continue
        if value < minimum:
            print(f"Value must be at least {minimum}.")
        elif maximum is not None and value > maximum:
            print(f"Value must be no more than {maximum}.")
        else:
            return value


def search_routes(db):
    heading("FIND YOUR JOURNEY")
    term = input("Enter route ID or city name: ").strip().casefold()
    if not term:
        print("Search cannot be empty.")
        return
    matches = []
    for route, available in all_routes(db):
        fields = (route["route_id"], route["departure_city"], route["destination_city"])
        if any(term in field.casefold() for field in fields):
            matches.append((route, available))
    print_routes(db, rows=matches)


def book_ticket(db):
    print_routes(db, available_only=True)
    heading("BOOK A TICKET")
    name = prompt_nonempty("Passenger full name: ")
    age = prompt_int("Passenger age: ", 1, 120)
    route_id = input("Route ID: ").strip().upper()
    route = get_route(db, route_id)
    if route is None:
        print("❌ Route ID not found. Booking was not created.")
        return

    available = route_available_seats(db, route["route_id"])
    if available <= 0:
        print("❌ This bus is fully booked.")
        return
    seats = prompt_int(f"Seats required (available {available}): ", 1, available)
    total = seats * route["ticket_price"]

    print("\nBooking summary")
    line()
    print(f"Passenger : {name}")
    print(f"Journey   : {route['departure_city']} → {route['destination_city']}")
    print(f"Departure : {route['departure_time']}")
    print(f"Seats     : {seats}")
    print(f"Total fare: {money(total)}")
    line()
    confirm = input("Confirm booking? (y/n): ").strip().lower()
    if confirm not in ("y", "yes"):
        print("Booking cancelled before saving.")
        return

    now = datetime.now()
    with db:
        last = db.execute(
            "SELECT MAX(CAST(SUBSTR(booking_id, 2) AS INTEGER)) FROM bookings"
        ).fetchone()[0]
        booking_id = f"B{max(1000, last or 1000) + 1}"
        db.execute(
            """INSERT INTO bookings
               (booking_id, passenger_name, passenger_age, route_id, seats,
                total_fare, status, created_at)
               VALUES (?, ?, ?, ?, ?, ?, 'Confirmed', ?)""",
            (booking_id, name, age, route["route_id"], seats, total, now.strftime("%Y-%m-%d %H:%M")),
        )

    print("\n✅ BOOKING CONFIRMED")
    line()
    print(f"Booking ID : {booking_id}")
    print(f"Passenger  : {name}")
    print(f"Route      : {route['departure_city']} → {route['destination_city']}")
    print(f"Seats      : {seats}")
    print(f"Total fare : {money(total)}")
    print("Status     : CONFIRMED")
    print("Keep your booking ID for lookup or cancellation.")
    line()


def view_bookings(db):
    heading("BOOKING HISTORY")
    term = input("Enter booking ID or passenger name (blank = all): ").strip()
    sql = """SELECT b.*, r.departure_city, r.destination_city, r.departure_time
             FROM bookings b JOIN routes r ON r.route_id = b.route_id"""
    rows = db.execute(sql + " ORDER BY b.created_at DESC, b.booking_id DESC").fetchall()
    if term:
        key = term.casefold()
        rows = [b for b in rows if key in b["booking_id"].casefold()
                or key in b["passenger_name"].casefold()]
    if not rows:
        print("No bookings found.")
        return
    for b in rows:
        print(f"\n{b['booking_id']} | {b['status']}")
        print(f"  {b['passenger_name']} (age {b['passenger_age']})")
        print(f"  {b['departure_city']} → {b['destination_city']} at {b['departure_time']}")
        print(f"  Seats: {b['seats']} | Fare: {money(b['total_fare'])} | Date: {b['created_at']}")


def cancel_booking(db):
    heading("CANCEL A BOOKING")
    booking_id = input("Booking ID (e.g. B1001): ").strip().upper()
    booking = db.execute("SELECT * FROM bookings WHERE booking_id = ?", (booking_id,)).fetchone()
    if not booking:
        print("❌ Booking ID not found.")
        return
    if booking["status"] == "Cancelled":
        print("This booking is already cancelled. Seats were already released.")
        return
    print(f"Passenger: {booking['passenger_name']} | Seats: {booking['seats']} | Fare: {money(booking['total_fare'])}")
    if input("Confirm cancellation? (y/n): ").strip().lower() not in ("y", "yes"):
        print("Cancellation aborted.")
        return
    with db:
        db.execute("UPDATE bookings SET status = 'Cancelled' WHERE booking_id = ?", (booking_id,))
    print(f"✅ Booking {booking_id} cancelled. {booking['seats']} seat(s) are available again.")


def show_availability(db):
    heading("LIVE SEAT AVAILABILITY")
    for route, available in all_routes(db):
        total = route["total_seats"]
        used = total - available
        percent = (used / total) * 100
        status = "FULL" if available == 0 else ("LIMITED" if available <= 5 else "AVAILABLE")
        bar = "█" * int(percent // 5) + "░" * (20 - int(percent // 5))
        print(f"{route['route_id']}  {route['departure_city']} → {route['destination_city']}")
        print(f"  [{bar}] {available}/{total} seats free | {status}")


def booking_report(db):
    heading("ADMIN DASHBOARD / BOOKING REPORT")
    total = db.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]
    confirmed = db.execute("SELECT COUNT(*) FROM bookings WHERE status='Confirmed'").fetchone()[0]
    cancelled = db.execute("SELECT COUNT(*) FROM bookings WHERE status='Cancelled'").fetchone()[0]
    seats = db.execute("SELECT COALESCE(SUM(seats),0) FROM bookings WHERE status='Confirmed'").fetchone()[0]
    revenue = db.execute("SELECT COALESCE(SUM(total_fare),0) FROM bookings WHERE status='Confirmed'").fetchone()[0]
    print(f"Bookings created      : {total}")
    print(f"Confirmed bookings    : {confirmed}")
    print(f"Cancelled bookings    : {cancelled}")
    print(f"Seats currently sold  : {seats}")
    print(f"Confirmed revenue     : {money(revenue)}")
    print()
    print("ROUTE PERFORMANCE")
    line()
    for route, available in all_routes(db):
        booked = route["total_seats"] - available
        revenue_route = db.execute(
            "SELECT COALESCE(SUM(total_fare),0) FROM bookings WHERE route_id=? AND status='Confirmed'",
            (route["route_id"],),
        ).fetchone()[0]
        print(f"{route['route_id']} {route['departure_city']} → {route['destination_city']}: "
              f"{booked}/{route['total_seats']} seats | {money(revenue_route)} revenue")


def route_schedule(db):
    heading("ROUTE SCHEDULE")
    for city in CITIES:
        print(f"\n{city}")
        found = False
        for route, _ in all_routes(db):
            if route["departure_city"] == city:
                print(f"  {route['route_id']} → {route['destination_city']} | "
                      f"{route['departure_time']} | {money(route['ticket_price'])}")
                found = True
        if not found:
            print("  No scheduled departures.")


def main():
    initialize_database()
    actions = {
        "1": ("View bus routes", lambda db: print_routes(db)),
        "2": ("Search routes", search_routes),
        "3": ("Book a ticket", book_ticket),
        "4": ("View / find bookings", view_bookings),
        "5": ("Cancel a booking", cancel_booking),
        "6": ("Seat availability", show_availability),
        "7": ("Admin report", booking_report),
        "8": ("Route schedule", route_schedule),
    }

    while True:
        print("\n")
        line("═")
        print("        🚌 SMART BUS — TICKET BOOKING SYSTEM")
        print("                 HACKATHON EDITION")
        line("═")
        for key, (label, _) in actions.items():
            print(f"  {key}. {label}")
        print("  9. Exit")
        line()
        choice = input("Choose an option (1–9): ").strip()
        if choice == "9":
            print("Thank you for choosing Smart Bus. Safe travels! 🚌")
            break
        action = actions.get(choice)
        if action:
            try:
                action[1](connect())
            except sqlite3.Error as exc:
                print(f"Database error: {exc}")
            except (KeyboardInterrupt, EOFError):
                print("\nAction interrupted safely.")
        else:
            print("Invalid option. Please choose a number from 1 to 9.")


if __name__ == "__main__":
    main()
