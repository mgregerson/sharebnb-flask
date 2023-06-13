import jwt
from dotenv import load_dotenv
import os

load_dotenv()

secret = os.environ['SECRET_KEY']

def create_jwt(username):
    """Creates jwt for user"""

    payload = {
        "username": username
    }
    token = jwt.encode(payload, secret, algorithm="HS256")


    return token

# import jwt
# >>> encoded_jwt = jwt.encode({"some": "payload"}, "secret", algorithm="HS256")
# >>> print(encoded_jwt)
# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzb21lIjoicGF5bG9hZCJ9.4twFt5NiznN84AWoo1d7KO1T_yoc0Z6XOpOVswacPZg
# >>> jwt.decode(encoded_jwt, "secret", algorithms=["HS256"])
# {'some': 'payload'}

# function createToken(user) {
#   console.assert(user.isAdmin !== undefined,
#       "createToken passed user without isAdmin property");

#   let payload = {
#     username: user.username,
#     isAdmin: user.isAdmin || false,
#   };

#   return jwt.sign(payload, SECRET_KEY);
# }