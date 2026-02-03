from datetime import datetime,timedelta
from jose import jwt,JWTError

SECRET_KEY="THIS_IS_THE_SECRET_KEY"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


class JWTService:

    @staticmethod
    def create_access_token(user_id:str)->str:
        payload={
            "sub":user_id,
            "exp":datetime.now()+timedelta(ACCESS_TOKEN_EXPIRE_MINUTES)
        }
        return jwt.encode(payload,SECRET_KEY,algorithm=ALGORITHM)
    

    @staticmethod
    def decode_token(token:str)->str:
        try:
            payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
            return payload["sub"]
        except JWTError:
            return None
