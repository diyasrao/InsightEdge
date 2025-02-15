import secrets
from datetime import datetime, timedelta

from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.security.oauth2 import OAuth2PasswordBearer
from jose import JWTError, jwt

from fastapi import FastAPI,Depends, HTTPException, status, Request
from ..schema import schemas


from app.database import databasem
from bson import ObjectId
from app.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define OAuth2 security scheme for token-based authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# Create a HTTPBasic security object to use in the get_swagger_access function
security = HTTPBasic()

app = FastAPI()



def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt




def verify_access_token(token: str, credentials_exception):
    try:
        # Log the received token
        logger.info(f"Received token: {token}")

        # Remove the "Bearer" prefix if present
        if token.startswith("Bearer "):
            token = token[len("Bearer "):]
        
        # Remove any extra whitespace or brackets
        token = token.strip().strip("[]")
        
        logger.info(f"Extracted token: {token}")

        # Decode the token
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        logger.info(f"Decoded Payload: {decoded_token}")

        # Extract token data
        token_data = schemas.TokenData(id=decoded_token.get("sub"))  # Ensure it matches "sub"
        logger.info(f"Token Data ID: {token_data.id}")

        if token_data.id is None:
            logger.error("Token data ID is None")
            raise credentials_exception
    except JWTError as e:
        logger.error(f"Error decoding token: {e}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise credentials_exception

    logger.info(f"Valid Token Data: {token_data}")
    return token_data


def get_current_user(request: Request, db=Depends(databasem.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = request.headers.get("Authorization")
    logger.info(f"Received token: {token}")

    if not token:
        logger.error("No token provided")
        raise credentials_exception
    
    token = token.replace("Bearer ", "")
    logger.info(f"Extracted token: {token}")
    
    try:
        token_data = verify_access_token(token, credentials_exception)
        print(f"Decoded Token: {token_data}")
    except JWTError as e:
        logger.error(f"Error verifying access token: {e}")
        raise credentials_exception
    
    try:
        obj_id = ObjectId(token_data.id)
        logger.info(f"Extracted User ID: {obj_id}")
    except Exception as e:
        logger.error(f"Error converting token id to ObjectId: {e}")
        raise credentials_exception
    
    user = db.users.find_one({"_id": obj_id})
    
    if not user:
        logger.error("User not found in database")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    logger.info(f"Retrieved user: {user}")
    return user



def get_swagger_access(request: Request, credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(
        credentials.username, settings.SWAGGER_USERNAME)

    correct_password = secrets.compare_digest(
        credentials.password, settings.SWAGGER_PASSWORD)

    if not (correct_username and correct_password):
        bad_credentials = {
            "username": credentials.username,
            "password": credentials.password,
            "ip_address": request.client.host,
            "port": request.client.port
        }
        # print(bad_credentials)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username 
