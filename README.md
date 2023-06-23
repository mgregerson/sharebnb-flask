# Sharebnb Backend

This is the backend application for Sharebnb, a platform for sharing and booking rentals. It is built using Flask, a Python web framework.

## Installation

1. Clone the repository:

```shell
git clone git@github.com:mgregerson/sharebnb-flask.git
```

2. Set up dev environment and install the required dependencies:

```shell
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Set up the environment variables:

- Create a `.env` file in the root directory and add the following variables:

SECRET_KEY=<your-secret-key>
DATABASE_URL=<your-database-url>

4. Run the application:

```shell
flask run 
```

If on a newer mac, run:

```shell
flask run -p 5001
```

5. The backend server will start running on `http://127.0.0.1:<port>`, where `<port>` is the port number specified in `app.py`.

## Files and Directories

- **app.py**: This is the main Flask application file. It sets up the routes and handles user signup/login, rentals, reservations, messages, and conversations.

- **models.py**: This file defines the database models using SQLAlchemy. It includes the `User`, `Rental`, `Reservation`, `Message`, and `Conversation` models.

- **aws.py**: This file contains functions for uploading and downloading files to/from an AWS S3 bucket.

- **helpers.py**: This file provides helper functions used in the application, such as creating JSON Web Tokens (JWT).

- **rental_pics/**: This directory is used for storing rental photos uploaded by users.

## API Endpoints

- **POST /signup**: Allows a user to sign up by providing username, password, email, location, bio, and profile image.

- **POST /login**: Handles user login by verifying the username and password.

- **GET /rentals**: Returns JSON data of all rentals.

- **POST /rentals/<username>/add**: Allows a user to add a new rental by providing the rental details.

- **GET /rentals/<username>**: Returns JSON data of all rentals for a single user.

- **GET /rentals/<rental_id>**: Returns JSON data of a single rental.

- **GET /users/<username>**: Returns JSON data of a user and all their rentals.

- **GET /reservations/<username>**: Returns JSON data of all reservations for a user.

- **GET /reservations/<username>/<reservation_id>**: Returns JSON data of a single reservation.

- **POST /reservations/<username>/add**: Allows a user to add a new reservation.

- **GET /messages/<username>**: Returns JSON data of all messages for a user.

- **GET /messages/<username>/<message_id>**: Returns JSON data of a single message.

- **POST /messages**: Sends a message from one user to another.

- **POST /conversations**: Creates a conversation between two users.

- **GET /conversations/<username>**: Returns JSON data of all conversations for a user.

- **GET /conversations/<conversation_id>/messages**: Returns JSON data of all messages in a conversation.

- **GET /conversations/<sender>/<recipient>/messages**: Returns JSON data of all messages in a conversation between two users.

## Models

The application uses the following database models:

- **User**: Represents a user in the system. It has attributes like `username`, `email`, `image_url`, `bio`, `location`, and `password`.

- **Rental**: Represents a rental listing. It includes fields like `description`, `location`, `price`, and `url`.

- **Reservation**: Represents a booking reservation made by a user

- **Message**: Represents an individual message from one user to another

- **Conversation**: Represents a conversation between two users.

## Contributing

Contributions to the ShareBnb app are welcome! If you find any bugs or have suggestions for new features, please open an issue or submit a pull request.

## License

The ShareBnb app is open-source and released by me, Matt Gregerson. Enjoy!
