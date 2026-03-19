"""
Run once to create all tables and seed some sample slots.
Usage: python init_db.py
"""
from datetime import date, time, timedelta
from app import create_app, db
from app.models import User, Slot, Booking

app = create_app()

with app.app_context():
    db.create_all()
    print("✓ Tables created.")

    # Seed slots for next 7 days, 9am–5pm every 30 mins
    today = date.today()
    added = 0
    for day_offset in range(7):
        slot_date = today + timedelta(days=day_offset)
        hour = 9
        minute = 0
        while hour < 17:
            start = time(hour, minute)
            end_minute = minute + 30
            end_hour = hour
            if end_minute >= 60:
                end_minute -= 60
                end_hour += 1
            end = time(end_hour, end_minute)

            exists = Slot.query.filter_by(date=slot_date, start_time=start).first()
            if not exists:
                s = Slot(date=slot_date, start_time=start, end_time=end, capacity=1)
                db.session.add(s)
                added += 1

            minute += 30
            if minute >= 60:
                minute = 0
                hour += 1

    db.session.commit()
    print(f"✓ {added} slots seeded for the next 7 days.")
    print("Done! Run 'python run.py' to start the server.")