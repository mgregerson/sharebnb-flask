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

    user_sent_messages = db.relationship('Message', backref='sender_user', foreign_keys='Message.sender_username')

    user_received_messages = db.relationship('Message', backref='recipient_user', foreign_keys='Message.recipient_username')

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

    rental = db.relationship('Rental', backref='rating')

    def serialize(self):
        """Serialize to dictionary."""

        return {
            "id": self.id,
            "rating": self.rating,
            "rental_id": self.rental_id
        }

    @classmethod
    def add_rating(cls, rating, rental_id):
        """Class method to add a rating to the database"""

        rating = Rating(
            rating=rating,
            rental_id=rental_id
        )

        db.session.add(rating)
        return rating

class Reservation(db.Model):
    """Reservation on each rental"""

    __tablename__ = 'reservations'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    start_date = db.Column(
        db.String(50),
        nullable=False
    )

    end_date = db.Column(
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
    def add_reservation(cls, start_date, end_date, rental_id, renter, rating=None):
        """Class method to add a reservation to the database"""

        reservation = Reservation(
            start_date=start_date,
            end_date=end_date,
            rental_id=rental_id,
            renter=renter,
            rating=rating,
        )

        db.session.add(reservation)
        return reservation

    def serialize(self):
        """Serialize to dictionary"""

        return {
            "id": self.id,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "rating": self.rating,
            "rental_id": self.rental_id,
            "renter": self.renter
        }


class Message(db.Model):
    """ Messages table """

    __tablename__ = 'messages'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    content = db.Column(
        db.Text,
        nullable=False
    )

    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    conversation_id = db.Column(
        db.Integer,
        db.ForeignKey('conversations.id', ondelete='CASCADE'),
        nullable=False
    )

    conversation = db.relationship('Conversation', backref='messages')

    sender_username = db.Column(
        db.Text,
        db.ForeignKey('users.username', ondelete='CASCADE'),
        nullable=False
    )

    sender = db.relationship('User', backref='sent_messages', foreign_keys=[sender_username])

    recipient_username = db.Column(
        db.Text,
        db.ForeignKey('users.username', ondelete='CASCADE'),
        nullable=False
    )

    recipient = db.relationship('User', backref='received_messages', foreign_keys=[recipient_username])

    @classmethod
    def create_message(cls, content, sender_username, recipient_username, conversation_id):
        """Create a new message and add it to the database."""

        message = Message(
            content=content,
            sender_username=sender_username,
            recipient_username=recipient_username,
            conversation_id=conversation_id
        )

        db.session.add(message)
        return message

    def serialize(self):
        """Serialize to dictionary."""

        return {
            "id": self.id,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "conversation_id": self.conversation_id,
            "sender_username": self.sender_username,
            "recipient_username": self.recipient_username
        }

    
class Conversation(db.Model):
    """ Conversations between users """

    __tablename__ = 'conversations'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user1_username = db.Column(
        db.Text,
        db.ForeignKey('users.username', ondelete='CASCADE'),
        nullable=False
    )

    user1 = db.relationship('User', foreign_keys=[user1_username])

    user2_username = db.Column(
        db.Text,
        db.ForeignKey('users.username', ondelete='CASCADE'),
        nullable=False
    )

    user2 = db.relationship('User', foreign_keys=[user2_username])

    @classmethod
    def create_conversation(cls, user1_username, user2_username):
        """Create a new conversation between two users and add it to the database."""

        conversation = Conversation(
            user1_username=user1_username,
            user2_username=user2_username
        )

        db.session.add(conversation)
        return conversation

    def serialize(self):
        """Serialize to dictionary."""

        return {
            "id": self.id,
            "user1_username": self.user1_username,
            "user2_username": self.user2_username
        }

def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    app.app_context().push()
    db.app = app
    db.init_app(app)