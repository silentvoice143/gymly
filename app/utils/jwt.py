from datetime import datetime, timedelta
from jose import jwt

SECRET_KEY = "SUPER_SECRET_GYMLY_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 Day


# dict can be ie data : { "user_id": 5, "role": "user" }
def create_access_token(data: dict):
    to_encode = data.copy() # copy the data so otiginal dict not get modified
    to_encode["exp"] = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) # added the exp in the data it is standard for jwt
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) 
