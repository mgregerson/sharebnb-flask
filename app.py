from flask import Flask, request, redirect, render_template, flash, jsonify
from flask_cors import CORS
from werkzeug.exceptions import Unauthorized
from flask_debugtoolbar import DebugToolbarExtension
import os
from dotenv import load_dotenv
from models import db, connect_db, User, Rental, Reservation, Message, Conversation
from sqlalchemy import and_, or_
from helpers import create_jwt
import base64
from io import BytesIO
from PIL import Image
from aws import upload_file, download


BASE_URL = "http://127.0.0.1:"

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True

debug = DebugToolbarExtension(app)

connect_db(app)


DEFAULT_IMAGE_URL = "/static/images/default_profile_img.png"


def decode_and_upload_photo(photo_data):
    """Decodes a 64byte photo and uploads to s3 bucket"""

    url = photo_data['url']
    #TODO: Grab the mimetype off of the URL (Look up a module to do so)

    # returned_bytes = photo_data['bytes'][index:]

    returned_bytes = photo_data['bytes'].split(',', 1)[1].strip()

    img_bytes = base64.b64decode(returned_bytes)
    img_io = BytesIO(img_bytes)

    with open(f'rental_pics/{url}', 'wb') as f:
        f.write(img_io.read())

    upload_file(f'rental_pics/{url}')

    os.remove(f'rental_pics/{url}')

# def download_and_encode_photo(image_url):
#     """Downloads photo from s3 and encodes it to 64-bits to send in json

#     CHANGED TO IMAGE_URL DIRECTLY"""

#     photo_download = download(image_url) #backyard.jpeg

#     with open(f'rental_pics/{image_url}', 'wb') as f:
#         encoded_string = base64.b64encode(f.read())
#     # bytes_url = bytes(image_url, 'utf-8')

#     # encoded_photo = base64.b64encode(bytes_url)

#     # print('encoded-photo:', encoded_photo)

#     return encoded_string


##############################################################################
# User signup/login

@app.post('/signup')
def signup():
    """Handle user signup."""

    user_data  = request.get_json()

    if (user_data['image_url'] != ''):
        User.signup(
            username=user_data['username'],
            password=user_data['password'],
            email=user_data['email'],
            location=user_data['location'] or None,
            bio=user_data['bio'] or None,
            image_url=user_data['image_url'],
        )
    else:
        user_data['image_url'] = DEFAULT_IMAGE_URL

        User.signup(
            username=user_data['username'],
            password=user_data['password'],
            email=user_data['email'],
            location=user_data['location'] or None,
            bio=user_data['bio'] or None,
            image_url=user_data['image_url'],
        )

    db.session.commit()

    token = create_jwt(user_data["username"])

    return jsonify(token=token)

@app.post('/login')
def login():
    """Handle user login"""

    login_data = request.get_json()
    login_status = User.authenticate(username=login_data['username'],
                                     password=login_data['password'])

    if (login_status is False):
        return Unauthorized()

    token = create_jwt(login_data["username"])

    return jsonify(token=token)

##############################################################################
# Rentals routes:

@app.get('/rentals')
def get_rentals():
    """Returns json data of all rentals"""
    rentals = Rental.query.all()
    serialized = [r.serialize() for r in rentals]

    return jsonify(rentals=serialized)

@app.post('/rentals/<username>/add')
def add_rental(username):
    """Allows a user to add a new rental"""

    rental = request.get_json()

    photo_data = rental['rentalPhotos']

    decode_and_upload_photo(photo_data)

    rd = rental['rentalData']

    rental_data = Rental.add_rental(
        description=rd['description'],
        location=rd['location'],
        price=int(rd['price']),
        owner_username=username,
        url=rd['url']
    )

    db.session.commit()

    serialized = rental_data.serialize()

    return jsonify(rental=serialized)

@app.get('/rentals/<username>')
def get_user_rentals(username):
    """Returns json data of all rentals for a single user"""

    user = User.query.get_or_404(username)

    rentals = user.rentals

    serialized = [r.serialize() for r in rentals]

    return jsonify(rentals=serialized)

@app.get('/rentals/<int:rental_id>')
def get_user_rental(rental_id):
    """Returns json data of single user's rental"""

    rental = Rental.query.filter(
        and_(Rental.id == rental_id)
    ).first()

    if (not rental):
        return jsonify(rental=None)

    serialized = rental.serialize()

    return jsonify(rental=serialized)



# @app.patch('/rentals/<username>/<int:rental_id>', methods=['PATCH'])
# def edit_rental():
#     """Allows a user to edit a rental"""

#     return "/rentals/<username>/<int:rental_id>"

# @app.post('/rentals/<int:rental_id>/new-reservation')
# def add_reservation():
#     """Allows a user to book a new reservation"""

#     return '/rentals/<int:rental_id>/new-reservation'

##############################################################################
# User routes:

@app.get('/users/<username>')
def get_user(username):
    """Returns json data a user + all rentals they have"""
    user = User.query.get_or_404(username)
    serialized_user = user.serialize()
    rentals = Rental.query.filter(Rental.owner_username == username).all()
    serialized_rentals = [r.serialize() for r in rentals]

    return jsonify(user=serialized_user, rentals=serialized_rentals)


##############################################################################
# Reservations routes:

@app.get('/reservations/<username>/')
def get_user_reservations(username):
    """Returns json data of all of a user's reservations"""

    reservations = Reservation.query.filter(Reservation.renter == username)
    serialized = [r.serialize() for r in reservations]

    return jsonify(reservations=serialized)

@app.get('/reservations/<username>/<int:reservation_id>')
def get_user_reservation(username, reservation_id):
    """Returns json data of a single user reservation"""

    reservation = Reservation.query.filter(
        and_(Reservation.renter == username, Reservation.id == reservation_id)
    ).first()

    if (not reservation):
        return jsonify(reservation=None)

    serialized = reservation.serialize()

    return jsonify(reservation=serialized)

@app.post('/reservations/<username>/add')
def add_reservation(username):
    """Allows a user to add a new reservation"""

    reservation_data = request.get_json()

    start_date = reservation_data['start_date']
    end_date = reservation_data['end_date']
    rental_id = reservation_data['rental_id']
    rating = reservation_data.get('rating')

    if rating is not None:
        # Rating is provided
        reservation = Reservation.add_reservation(start_date=start_date, end_date=end_date, rental_id=rental_id, renter=username, rating=rating)
    else:
        # Rating is not provided
        reservation = Reservation.add_reservation(start_date=start_date, end_date=end_date, rental_id=rental_id, renter=username)

    db.session.commit()

    serialized = reservation.serialize()

    return jsonify(reservation=serialized)

##############################################################################
# Messages routes:

@app.get('/messages/<username>')
def get_user_messages(username):
    """Returns JSON data of all messages for a single user"""

    user = User.query.get_or_404(username)

    sent_messages = Message.query.filter_by(sender=user).all()
    received_messages = Message.query.filter_by(recipient=user).all()

    serialized = [message.serialize() for message in sent_messages] + [message.serialize() for message in received_messages]

    return jsonify(messages=serialized)

@app.get('/messages/<username>/<int:message_id>')
def get_user_message(username, message_id):
    """Returns JSON data of a single user's message"""

    message = Message.query.filter_by(sender=username, id=message_id).first()

    if not message:
        return jsonify(message=None)

    serialized = message.serialize()

    return jsonify(message=serialized)

@app.post('/messages')
def send_message():
    data = request.get_json()

    if 'sender' not in data or 'recipient' not in data or 'content' not in data:
        return jsonify(message='Missing required fields'), 400

    sender_username = data['sender']
    receiver_username = data['recipient']
    message_text = data['content']

    sender = User.query.filter_by(username=sender_username).first()
    recipient = User.query.filter_by(username=receiver_username).first()

    if not sender or not recipient:
        return jsonify(message='Sender or receiver not found'), 404

    conversation = Conversation.query.filter(
        or_(
            and_(Conversation.user1 == sender, Conversation.user2 == recipient),
            and_(Conversation.user1 == recipient, Conversation.user2 == sender)
        )
    ).first()

    if not conversation:
        conversation = Conversation(user1=sender, user2=recipient)
        db.session.add(conversation)

    message = Message(content=message_text, sender=sender, recipient=recipient, conversation=conversation)
    db.session.add(message)
    db.session.commit()

    messages = Message.query.filter_by(conversation=conversation).order_by(Message.timestamp).all()

    # Serialize messages to dictionary format
    serialized_messages = [msg.serialize() for msg in messages]

    return jsonify(conversation=serialized_messages), 200

##############################################################################
# Conversations routes:

@app.post('/conversations')
def create_conversation():
    """Create a conversation between two users"""

    conversation_data = request.get_json()
    user1_username = conversation_data['user1']
    user2_username = conversation_data['user2']

    # Check if a conversation already exists between the users
    existing_conversation = Conversation.query.filter(
        Conversation.user1.has(username=user1_username),
        Conversation.user2.has(username=user2_username)
    ).first()

    if existing_conversation is not None:
        return jsonify(error='Conversation already exists')

    # Create new conversation
    user1 = User.query.filter_by(username=user1_username).first()
    user2 = User.query.filter_by(username=user2_username).first()

    if user1 is None or user2 is None:
        return jsonify(error='Invalid user')

    conversation = Conversation(user1=user1, user2=user2)
    db.session.add(conversation)
    db.session.commit()

    return jsonify(conversation=conversation.serialize())

@app.get('/conversations/<username>')
def get_user_conversations(username):
    """Returns JSON data of all conversations for a single user"""

    user = User.query.get_or_404(username)

    conversations = Conversation.query.filter(or_(Conversation.user1 == user, Conversation.user2 == user)).all()

    serialized = [conversation.serialize() for conversation in conversations]

    return jsonify(conversations=serialized)

@app.get('/conversations/<int:conversation_id>/messages')
def get_conversation_messages_by_id(conversation_id):
    """Returns JSON data of all messages in a single conversation"""

    conversation = Conversation.query.get_or_404(conversation_id)

    messages = conversation.messages
    messages.sort(key=lambda m: m.timestamp)  # Sort messages by timestamp

    serialized = [message.serialize() for message in messages]

    return jsonify(messages=serialized)

@app.get('/conversations/<sender>/<recipient>/messages')
def get_conversation_messages_by_users(sender, recipient):
    """Returns JSON data of all messages in a conversation between the sender and recipient"""

    conversation = Conversation.query.filter(
        Conversation.user1.has(username=sender) & Conversation.user2.has(username=recipient)
    ).first()

    if not conversation:
        return jsonify(messages=[])

    messages = conversation.messages
    serialized_messages = [message.serialize() for message in messages]

    return jsonify(messages=serialized_messages)


