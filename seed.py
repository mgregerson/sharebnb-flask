from app import db
from models import db, connect_db, User, Rental, Reservation

db.drop_all()
db.create_all()

# Add Users
john = User.signup('john_doe', 'john@example.com', 'password', 'San Francisco, CA', 'I am a software engineer', 'https://example.com/john.jpg')
jane = User.signup('jane_doe', 'jane@example.com', 'password', 'San Francisco, CA', 'I am a software engineer', 'https://example.com/jane.jpg')
alex = User.signup('alex_smith', 'alex@example.com', 'password', 'New York, NY', 'I am a software engineer', 'https://example.com/alex.jpg')

db.session.commit()

# Add Rentals

miami = Rental.add_rental('Beautiful beachside backyard', 'Miami, FL', 1500, 'john_doe', '')
ny = Rental.add_rental('Patio on Upper East Side', 'NY, NY', 1000, 'alex_smith', '')
sf = Rental.add_rental('Private park!', 'San Francisco, CA', 2000, 'jane_doe', '')

db.session.commit()

# Add Reservations

pool_party = Reservation.add_reservation(date='2/6/2023', rental_id=1, renter='jane_doe', rating=5)
cookout = Reservation.add_reservation(date='6/1/2023', rental_id=2, renter='john_doe')
flag_football = Reservation.add_reservation(date='2/10/2023', rental_id=3, renter='alex_smith', rating=3)

db.session.commit()