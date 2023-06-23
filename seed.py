from app import db
from models import db, connect_db, User, Rental, Reservation, Message, Conversation

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

pool_party = Reservation.add_reservation(start_date='2/6/2023', end_date='2/6/2023', rental_id=1, renter='jane_doe', rating=5)
cookout = Reservation.add_reservation(start_date='6/1/2023', end_date='6/1/2023', rental_id=2, renter='john_doe')
flag_football = Reservation.add_reservation(start_date='2/10/2023', end_date='2/10/2023', rental_id=3, renter='alex_smith')

db.session.commit()

# Add Conversations

conversation1 = Conversation.create_conversation(user1_username='john_doe', user2_username='jane_doe')
conversation2 = Conversation.create_conversation(user1_username='john_doe', user2_username='alex_smith')
conversation3 = Conversation.create_conversation(user1_username='jane_doe', user2_username='alex_smith')

db.session.commit()

# Add Messages
message1 = Message.create_message(content='Hi Jane, how are you?', sender_username='john_doe', recipient_username='jane_doe', conversation_id=conversation1.id)
message2 = Message.create_message(content='Hey John, I am doing great!', sender_username='jane_doe', recipient_username='john_doe', conversation_id=conversation1.id)
message3 = Message.create_message(content='Hey John, want to grab lunch tomorrow?', sender_username='john_doe', recipient_username='alex_smith', conversation_id=conversation2.id)
message4 = Message.create_message(content='Sure, what time works for you?', sender_username='alex_smith', recipient_username='john_doe', conversation_id=conversation2.id)
message5 = Message.create_message(content='Hi Alex, how was your weekend?', sender_username='jane_doe', recipient_username='alex_smith', conversation_id=conversation3.id)
message6 = Message.create_message(content='Hey Jane, it was amazing! I went hiking.', sender_username='alex_smith', recipient_username='jane_doe', conversation_id=conversation3.id)

db.session.commit()