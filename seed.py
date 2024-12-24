from models import db, Venue, Artist, Show
from app import app
from datetime import datetime

with app.app_context():
    # Add 10 Venues
    venues = [
        Venue(
            name=f"Venue {i}",
            city="San Francisco",
            state="CA",
            address=f"Address {i}",
            phone=f"123-123-12{i}4",
            genres=["Jazz", "Classical", "Pop"],
            facebook_link="",
            image_link="",
            website="",
            seeking_talent=(i % 2 == 0),
            seeking_description=f"Looking for artists to perform at Venue {i}" if i % 2 == 0 else ""
        )
        for i in range(1, 9)
    ]

    # Add 10 Artists
    artists = [
        Artist(
            name=f"Artist {i}",
            city="City {i}",
            state="CA",
            phone=f"321-321-12{i}4",
            genres=["Rock n Roll", "Blues", "Pop"],
            facebook_link="",
            image_link="",
            website="",
            seeking_venue=(i % 2 != 0),
            seeking_description=f"Looking for venues to perform at Artist {i}" if i % 2 != 0 else ""
        )
        for i in range(1, 9)
    ]

    # Add 10 Shows
    shows = [
        Show(
            artist_id=i,
            venue_id=i,
            start_time=datetime(2024, 1, 10 + i, 20, 0, 0)
        )
        for i in range(1, 9)
    ]

    # Commit all to database
    db.session.add_all(venues)
    db.session.add_all(artists)
    db.session.add_all(shows)
    db.session.commit()

    print("Database successfully seeded with 10 venues, 10 artists, and 10 shows.")
