from flask import Flask, request, redirect, render_template, flash, jsonify
from flask_cors import CORS
from werkzeug.exceptions import Unauthorized
from flask_debugtoolbar import DebugToolbarExtension
import os
from dotenv import load_dotenv
from models import db, connect_db, User, Rental, Reservation
from sqlalchemy import and_
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





# TODO: Work on Messages
# /messages/username (All their messages)
# /messages/username/int:message-id (A single message)


