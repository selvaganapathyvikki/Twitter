import jwt
import bcrypt
from datetime import datetime, timedelta

def get_jwt_token(username):

    #creating a token 
    JWT_SECRET = "selvaganapathy"
    JWT_ALGORITHM = "HS256"
    dt = datetime.now() + timedelta(minutes=2)
    payload = {"name": username, 'exp': dt}
    token = jwt.encode(payload, JWT_SECRET,JWT_ALGORITHM)
    return token

def encrypt_password(password) :
    bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(bytes,salt)
    return hash.decode('utf-8')

def check_password(hashed_password, user_entered_password) :
    userBytes = user_entered_password.encode('utf-8')
    print(userBytes)
    result = bcrypt.checkpw(userBytes, hashed_password.encode('utf-8'))
    return result