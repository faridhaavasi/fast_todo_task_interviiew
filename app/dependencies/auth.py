
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.models.user import User

from app.core.database import get_db
from sqlalchemy.orm import Session
from datetime import datetime, timedelta,timezone
import jwt
from jwt import ExpiredSignatureError, InvalidSignatureError, DecodeError
import time

from app.core.config import settings
security = HTTPBearer(auto_error=False)

SECRET_KEY = settings.JWT_SECRET_KEY
ALGO = "HS256"

def get_authenticated_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):

    # Check if credentials are not provided
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed, token not provided",
        )

    token = credentials.credentials
    try:
        decoded = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=ALGO
        )
        user_id = decoded.get("user_id", None)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed, user_id not in the payload",
            )

        if decoded.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed, token type not valid",
            )
        if datetime.now() > datetime.fromtimestamp(decoded.get("exp")):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed, token expired",
            )

        user_obj = db.query(User).filter_by(id=user_id).one()
        return user_obj

    except InvalidSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed, invalid signature",
        )
    except DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed, decode failed",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed, {e}",
        )

def generate_access_token(user_id: int, expires_in: int = 60 * 5) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "type": "access",
        "user_id": user_id,
        "iat": now,
        "exp": now + timedelta(seconds=expires_in),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=ALGO)


def generate_refresh_token(user_id: int, expires_in: int = 3600 * 24) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "type": "refresh",
        "user_id": user_id,
        "iat": now,
        "exp": now + timedelta(seconds=expires_in),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")


def decode_refresh_token(token):
    try:
        decoded = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms="HS256"
        )
        user_id = decoded.get("user_id", None)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed, user_id not in the payload",
            )

        if decoded.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed, token type not valid",
            )
        if datetime.now() > datetime.fromtimestamp(decoded.get("exp")):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed, token expired",
            )

        return user_id

    except InvalidSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed, invalid signature",
        )
    except DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed, decode failed",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed, {e}",
        )



def generate_verify_token(user_id: int, expires_minutes: int = 30) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=expires_minutes)
    payload = {"type": "verify", "purpose": "verify_email", "user_id": user_id, "iat": now, "exp": exp}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGO)

def decode_verify_token(token: str) -> int:
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGO])
        if decoded.get("type") != "verify" or decoded.get("purpose") != "verify_email":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token purpose")
        return decoded.get("user_id")
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except InvalidSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token signature")
    except DecodeError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token decode failed")




def get_user_via_access_token(jwt_token_access_token: str, db: Session) -> User:
    payload = jwt.decode(jwt_token_access_token, settings.JWT_SECRET_KEY, algorithms=ALGO)
    if payload['exp'] < int(time.time()):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='Token expired')
    user = db.query(User).filter_by(id=payload['user_id']).one_or_none()
    if user:
        return user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')