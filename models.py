from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint
from datetime import datetime

bcrypt = Bcrypt()
db = SQLAlchemy()


class User(db.Model):
    """ User in the system """

    __tablename__ = 'users'

    def __repr__(self):
        return f"<User {self.username}>"

    username = db.Column(
        db.Text,
        nullable=False,
        primary_key=True,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    image_url = db.Column(
        db.Text,
        nullable=True,
    )

    bio = db.Column(
        db.Text,
    )

    location = db.Column(
        db.Text,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    rentals = db.relationship('Rental', backref='users')

    reservations = db.relationship('Reservation', backref='users')

    def serialize(self):
        """Serialize to dictionary."""

        return {
            "username": self.username,
            "email": self.email,
            "image_url": self.image_url,
            "bio": self.bio,
            "location": self.location
        }

    @classmethod
    def signup(cls, username, email, password, location, bio, image_url):
        """Sign up user. Hashes password and adds to db"""

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            location=location,
            bio=bio,
            image_url=image_url
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        If this can't find matching user (or if password is wrong), returns
        False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


class Rental(db.Model):
    """ Rentals available """

    __tablename__ = 'rentals'

    def __repr__(self):
        return f"<Rental #{self.id}: {self.description}>"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    description = db.Column(
        db.Text(),
        nullable=False
    )

    location = db.Column(
        db.String(100),
        nullable=False
    )

    price = db.Column(
        db.Integer,
        nullable=False
    )

    url = db.Column(
        db.String(100),
        nullable=True
    )

    owner_username = db.Column(
        db.Text,
        db.ForeignKey('users.username', ondelete='CASCADE'),
        nullable=False,
    )

    reservations = db.relationship('Reservation', backref='rentals')

    ratings = db.relationship('Rating', backref='rentals')

    @classmethod
    def add_rental(cls, description, location, price, owner_username, url):
        """Class method to add a rental to the database"""

        rental = Rental(
            description=description,
            location=location,
            price=price,
            owner_username=owner_username,
            url=url
        )

        db.session.add(rental)
        return rental

    def serialize(self):
        """Serialize to dictionary."""

        return {
            "id": self.id,
            "description": self.description,
            "location": self.location,
            "price": self.price,
            "owner_username": self.owner_username,
            "url": self.url
        }

class Rating(db.Model):
    """ Rating for each rental """

    __tablename__ = 'ratings'

    def __repr__(self):
        return f"<Rating #{self.id}: {self.rental_id} rating: {self.rating}>"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    rating = db.Column(
        db.Integer,
        nullable=False
    )

    rental_id = db.Column(
        db.Integer,
        db.ForeignKey('rentals.id', ondelete='CASCADE'),
        nullable=False,
    )

    def serialize(self):
        """Serialize to dictionary."""

        return {
            "id": self.id,
            "rating": self.rating,
            "rental_id": self.rental_id
        }

class Reservation(db.Model):
    """ Reservation on each rental """

    __tablename__ = 'reservations'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    date = db.Column(
        db.String(50),
        nullable=False
    )

    rating = db.Column(
        db.Integer,
        nullable=True
    )

    rental_id = db.Column(
        db.Integer,
        db.ForeignKey('rentals.id', ondelete='CASCADE'),
        nullable=False,
    )

    renter = db.Column(
        db.Text,
        db.ForeignKey('users.username', ondelete='CASCADE'),
        nullable=False
    )

    @classmethod
    def add_reservation(cls, date, rental_id, renter, rating=None):
        """Class method to add a rental to the database"""

        reservation = Reservation(
            date=date,
            rental_id=rental_id,
            renter=renter,
            rating=rating,
        )

        db.session.add(reservation)
        return reservation

    def serialize(self):
        """Serialize to dictionary."""

        return {
            "id": self.id,
            "date": self.date,
            "rating": self.rating,
            "rental_id": self.rental_id,
            "renter": self.renter
        }



def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    app.app_context().push()
    db.app = app
    db.init_app(app)