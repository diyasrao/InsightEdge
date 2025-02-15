from bson import ObjectId
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError,jwt
from pymongo.collection import Collection
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from ..utils import oauth2, utils
from ..utils.utils import generate_otp
from ..schema.schemas import VerifyOTP, EmailSchema, ResetPasswordRequest
import os
from typing import Optional

from pydantic import BaseModel, EmailStr, Field
from ..database import databasem
from ..schema import schemas
from fastapi.responses import JSONResponse
from ..config import Settings


import logging
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["Authentication"]
)

SMTP_SERVER = "smtp.gmail.com" 
SMTP_PORT = 587  
SENDER_EMAIL = os.getenv("MAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_a_user(user: schemas.UserCreate, 
                  db: Collection = Depends(databasem.get_db)):
    users_collection = db["users"]
    events_collection = db['events']
    try:
        user.email = user.email.lower()
        existing_verified_user = users_collection.find_one({"email": user.email, "verification_status": True})
        existing_non_verified_user = users_collection.find_one({"email": user.email, "verification_status": False})

        if existing_verified_user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                              detail=f"Email {user.email} has already been used to create an user")
            
        if not (existing_verified_user or existing_non_verified_user):
            if users_collection.find_one({"username": user.username}) is not None:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                  detail=f"username {user.username} has already been used to create an user")
            
        hashed_password = utils.hash(user.password)
        logging.info("password hashed successfully")

        new_user = {
            "firstname": user.firstname,
            "lastname": user.lastname,
            "username": user.username,
            "email": user.email,
            "public_profile": True,
            "password": hashed_password,
            "created_at": datetime.utcnow(),
            "verification_status": False,
        }

        if existing_non_verified_user:
            new_values = {"$set": new_user}
            users_collection.update_one({"email": user.email}, new_values)
        else:
            users_collection.insert_one(new_user)

        # Rest of the signup process
        otp = generate_otp()
        expiry_time = datetime.now() + timedelta(minutes=5)
        users_collection.update_one(
            {"email": user.email}, 
            {"$set": {"verifyOtp": otp, "otp_expiry": expiry_time}}
        )
        
        created_user = users_collection.find_one({"email": user.email})
        Event = {
            "event_type": "User_registration",
            "user_id": str(created_user["_id"]),
            "timestamp": datetime.utcnow()             
        }
        events_collection.insert_one(Event)

        send_verification_email(user.email, user.username, otp)

        return {
            "id": str(created_user["_id"]),
            "firstname": str(created_user['firstname']),
            "lastname": str(created_user['lastname']),
            "username": created_user["username"],
            "email": created_user["email"],
            "created_at": created_user["created_at"],
        }
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    

def send_verification_email(email: str, username: str, otp: str):
    try:
        message = MIMEMultipart()
        message["From"] = SENDER_EMAIL
        message["To"] = email
        message["Subject"] = "Please verify your Insight Edge account"
        message_body = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@300..700&family=Playwrite+HR+Lijeva:wght@100..400&display=swap');
            </style>
            <title>OTP Verification</title>
            <style>
                body {{
                    font-family: 'Fredoka', sans-serif;
                    background: #f0f8ff;
                    margin: 0;
                    padding: 0;
                    color: #000000;
                }}
                .email-container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: linear-gradient(135deg, #d3d3d3, #f0f8ff);
                    border-radius: 10px;
                    padding: 30px;
                    color: #333;
                    box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
                }}
                .email-header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .logo-text {{
                    font-family: "Playwrite HR Lijeva", serif;
                    background: linear-gradient(to right, #cf23cf, #ff6b08, #f32170);
                    font-size: 2rem;
                    font-weight: 400;
                    color: transparent;
                    margin-bottom: 0;
                    background-clip: text;
                    -webkit-background-clip: text;
                }}
                .otp-box {{
                    background: #ffffff;
                    border-radius: 8px;
                    padding: 20px;
                    text-align: center;
                    font-size: 1.5rem;
                    letter-spacing: 2px;
                    font-weight: bold;
                    color: #36a69a;
                    margin: 20px 0;
                }}
                .button {{
                    background-color: #36a69a;
                    border-radius: 25px;
                    color: #ffffff;
                    padding: 15px 30px;
                    text-decoration: none;
                    font-size: 1rem;
                    display: inline-block;
                    margin-top: 30px;
                }}
                .button:hover {{
                    background-color: #30a08a;
                }}
                .email-body {{
                    text-align: center;
                }}
                .email-footer {{
                    margin-top: 40px;
                    text-align: center;
                    font-size: 0.9rem;
                    color: #666;
                }}
            </style>
        </head>
        <body>

            <div class="email-container">
                <div class="email-header">
                    <span class="logo-text" "email-container ">Insight Edge</span>
                </div>

                <div class="email-body">
                    <p>Hello <strong>{username}</strong>,</p>
                    <p>Your one-time OTP code to verify your account is:</p>
                    
                    <div class="otp-box">{otp}</div>

                    <p>Please use this OTP to complete your registration. The code is valid for <strong>5 minutes</strong>.</p>
                    <p>If you did not request this OTP, please ignore this email or contact support.</p>

                </div>

                <div class="email-footer">
                    <p>Thank you for choosing Insight Edge!</p>
                </div>
            </div>

        </body>
        </html>
        """
        message.attach(MIMEText(message_body, "html"))
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, EMAIL_PASSWORD)
            server.sendmail(SENDER_EMAIL, [email], message.as_string())
        logger.info("Verification email sent successfully")
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        raise HTTPException(status_code=500, detail="Could not send verification email")
    


public_email_services = ["gmail.com", "outlook.com"]
def is_valid_company_email(email: str) -> bool:
        email_domain = email.split("@")[-1]
        return email_domain not in public_email_services


@router.post("/verify-otp")
async def verify_otp(
    request: VerifyOTP, 
    db: Collection = Depends(databasem.get_db)
):
    try:
        request.email = request.email.lower()
        users_collection = db["users"]
        events_collection = db['events']

        # Find user and verify OTP
        user = users_collection.find_one({"verifyOtp": request.otp, "email": request.email})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Invalid OTP"
            )

        if user["otp_expiry"] < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="OTP has expired"
            )

        # Update verification status
        update_data = {
            "verification_status": True,
            "verifyOtp": None,
            "otp_expiry": None
        }

        users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": update_data}
        )

        # Create auth tokens
        access_token = oauth2.create_access_token(data={"sub": str(user["_id"])})
        refresh_token = oauth2.create_refresh_token(data={"sub": str(user["_id"])})
        
        # Store refresh token
        db["refresh_tokens"].insert_one({
            "user_id": str(user["_id"]),
            "refresh_token": refresh_token,
            "created_at": datetime.utcnow()
        })

        

        # Log first login event and send welcome email
        existing_login = events_collection.find_one({
            "user_id": str(user["_id"]), 
            "event_type": "Login"
        })
        
        if not existing_login:
            try:
                send_welcome_email(user['email'], user['username'])
            except Exception as e:
                logger.error(f"Could not send welcome email: {e}")

        # Log login event
        event_result = {
            "event_type": "Login",
            "user_id": str(user["_id"]),
            "timestamp": datetime.utcnow()
        }
        events_collection.insert_one(event_result)

        # Create response with tokens and user data
        response = JSONResponse(
            content={
                "message": f"{user['username']} registered successfully",
                "user": {
                    "id": str(user["_id"]),
                    "firstname": str(user['firstname']),
                    "lastname": str(user['lastname']),
                    "username": user["username"],
                    "email": user["email"],
                    "created_at": user["created_at"].isoformat() if user.get("created_at") else None,
                },
                "tokens": {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_type": "Bearer"
                }
            }
        )
        
        # Set access token cookie
        response.set_cookie(key="access_token", value=access_token)
        
        return response

    except Exception as e:
        logger.error(f"An error occurred in verify_otp: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def send_welcome_email(email: str, username: str):
    try:
        message = MIMEMultipart()
        message["From"] = SENDER_EMAIL
        message["To"] = email
        message["Subject"] = "Welcome to the Insign Edge"
        
        message_body = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@300..700&family=Playwrite+HR+Lijeva:wght@100..400&display=swap');
            </style>
            <style>
                body {{
                    font-family: 'Fredoka', sans-serif;
                    background: #f0f8ff;
                    margin: 0;
                    padding: 0;
                    color: #000000;
                }}
                .email-container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: linear-gradient(135deg, #d3d3d3, #f0f8ff);
                    border-radius: 10px;
                    padding: 30px;
                    color: #333;
                    box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
                }}
                .email-header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .logo-text {{
                    font-family: "Playwrite HR Lijeva", serif;
                    background: linear-gradient(to right, #cf23cf, #ff6b08, #f32170);
                    font-size: 2rem;
                    font-weight: 400;
                    color: transparent;
                    margin-bottom: 0;
                    background-clip: text;
                    -webkit-background-clip: text;
                }}
                .email-body {{
                    text-align: center;
                }}
                .feature-box {{
                    background-color: #ffffff;
                    border-radius: 8px;
                    padding: 5px;
                    margin: 10px 0;
                    box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
                    color: #333;
                }}
                .feature-box h3 {{
                    font-size: 1rem;
                    margin-bottom: 2px;
                }}
                .image-grid {{
                    width: 100%;
                    text-align: center;
                    margin-top: 30px;
                    margin-bottom: 30px;
                }}
                .image-grid td {{
                    width: 50%;
                    vertical-align: top;
                }}
                .image-grid img {{
                    width: 100%;
                    border-radius: 8px;
                    box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
                }}
                .email-footer {{
                    margin-top: 40px;
                    text-align: center;
                    font-size: 0.9rem;
                    color: #666;
                }}
            </style>
        </head>
        <body>

            <div class="email-container">
                <div class="email-header">
                    <span class="logo-text">Insight edge</span>
                </div>

                <div class="email-body">
                    <p style="color: #000000; background-color: transparent;">Hi {username},</p>
                    <p style="color: #000000; background-color: transparent;">Welcome to <span class="head-logo">Insight Edge</span>!</p>
                    <!-- Feature 1: AI Image Generation -->
                    <div class="feature-box">
                        <h3>🎨 AI Image Generation</h3>
                        <p>Bring your ideas to life with cutting-edge AI that creates breathtaking visuals from text prompts. Explore your creativity like never before!</p>
                    </div>

                    <!-- Feature 2: Image Editing Tools -->
                    <div class="feature-box">
                        <h3>🖌️ Image Editing Tools</h3>
                        <p>Fine-tune every detail of your creation with intuitive editing features. Make every image exactly how you envision it!</p>
                    </div>

                    <!-- Feature 3: Diverse Artistic Styles -->
                    <div class="feature-box">
                        <h3>🌈 Diverse Artistic Styles</h3>
                        <p>Explore a wide range of styles, from historic and classical art to futuristic and high-tech aesthetics. The possibilities are endless!</p>
                    </div>

                    <!-- Feature 4: Community & Networking -->
                    <div class="feature-box">
                        <h3>🌍 Community & Networking</h3>
                        <p>Share your art, connect with other creators, and get inspired by a global community of visionaries. There's always something new to discover!</p>
                    </div>

                    <p style="color: #000000; background-color: transparent;">Get started by logging into your account and explore all the cool features we have for you!</p>
                </div>

                <div class="email-footer">
                    <p>Thank you for choosing Insight Edge!</p>
                </div>
            </div>

        </body>
        </html>
        """
        message.attach(MIMEText(message_body, "html"))
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, EMAIL_PASSWORD)
            server.sendmail(SENDER_EMAIL, [email], message.as_string())
        logger.info("Welcome email sent successfully")
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        raise HTTPException(status_code=500, detail="Could not send welcome email")


@router.post("/login", response_model=schemas.Token)
def login_a_user(user_credentials: OAuth2PasswordRequestForm = Depends(), db:Collection = Depends(databasem.get_db)):
    logger.info("LOGIN Begin")
    try:
        user_credentials.username = user_credentials.username.lower()
        users_collection = db["users"]
        events_collection = db["events"]
        logger.info(f"Attempting to fetch user with email or username: {user_credentials.username}")
        
        user = users_collection.find_one({
            "$or": [
                {"email": user_credentials.username},
                {"username": {"$regex": f"^{user_credentials.username}$", "$options": "i"}}
            ]
        })

        logger.info(f"User Meta data {user_credentials.username} fetched successfully: {user}")
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="This email does not have an account"
            )
        if not utils.verify(user_credentials.password, user["password"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid credentials"
            )
        if not user["verification_status"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail = "This account is not verified try to register again"
            )
        logging.info("User password verified successfully")
        access_token = oauth2.create_access_token(
            data={"sub": str(user["_id"])}
        )
        refresh_token = oauth2.create_refresh_token(data={"sub": str(user["_id"])})
        db["refresh_tokens"].insert_one({
            "user_id": str(user["_id"]),
            "refresh_token": refresh_token,
            "created_at": datetime.utcnow()
        })
        logging.info("created access token successfully")

        response = JSONResponse(
            content={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "Bearer"
            }
        )
        response.set_cookie(key="access_token", value=access_token)
        logging.info("access token set in cookies")

        existing_login = events_collection.find_one({"user_id": str(user["_id"]), "event_type": "Login"})
        if not existing_login:
            try:
                send_welcome_email(user['email'], user['username'])
            except Exception as e:
                raise HTTPException(status_code=500, detail="Could not send welcome email")
            
        event_result = {
            "event_type": "Login",
            "user_id": str(user["_id"]),
            "timestamp": datetime.utcnow() 
        }
        result = events_collection.insert_one(event_result)
        logging.info("The log event saved in the db")

        return response
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/logout")
async def logout(
    current_user: dict = Depends(oauth2.get_current_user),
    db: Collection = Depends(databasem.get_db)
):
    try:
        users_collection = db["users"]
        db["refresh_tokens"].delete_many({"user_id": str(current_user["_id"])})
        
        return {"message": "Logged out successfully"}
    except Exception as e:
        logger.error(f"Error during logout: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/refresh-token")
def refresh_access_token(
    refresh_token: str,
    db: Collection = Depends(databasem.get_db)
):
    try:
        payload = jwt.decode(refresh_token, Settings.SECRET_KEY, algorithms=[Settings.ALGORITHM])
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        # Check if the refresh token exists in the database
        token_data = db["refresh_tokens"].find_one({"refresh_token": refresh_token})
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        # Generate a new access token
        access_token = oauth2.create_access_token(data={"sub": user_id})
        new_refresh_token = oauth2.create_refresh_token(data={"sub": user_id})

        db["refresh_tokens"].update_one(
            {"refresh_token": refresh_token},
            {"$set": {"refresh_token": new_refresh_token}}
        )

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "Bearer"
        }

    except JWTError as e:
        logger.error(f"Error decoding refresh token: {e}")
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


    
@router.delete("/delete-account", status_code=status.HTTP_200_OK)
async def delete_account(
    db: Collection = Depends(databasem.get_db), 
    current_user: dict = Depends(oauth2.get_current_user)
):
    try:
        user_id = current_user["_id"]
        str_user_id = str(user_id)

        # Initialize all collections
        users_collection = db["users"]
        events = db["events"]
        refresh_tokens = db["refresh_tokens"]

        # Start deletion process for each collection
        operations = {
            "refresh_tokens": refresh_tokens.delete_many({
                "user_id": str_user_id
            }),

            # Delete the user last
            "users": users_collection.delete_one({
                "_id": user_id
            })
        }

        deletion_results = {
            collection_name: operation.deleted_count
            for collection_name, operation in operations.items()
        }

        delete_event = {
            "event_type": "Account_Deletion",
            "user_id": str_user_id,
            "timestamp": datetime.utcnow(),
            "deletion_details": deletion_results
        }
        events.insert_one(delete_event)

        # Prepare response
        response = JSONResponse(
            content={
                "message": "Account and all associated data deleted successfully.",
                "deletion_details": deletion_results
            },
            status_code=status.HTTP_200_OK
        )
        
        response.delete_cookie(key="access_token")

        logger.info(f"Account deletion completed for user {str_user_id}. Details: {deletion_results}")
        return response

    except Exception as e:
        logger.error(f"An error occurred during account deletion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Account deletion failed: {str(e)}"
        )
    
    
@router.post("/forgot-password")
async def forgot_password(email: EmailSchema, db: Collection = Depends(databasem.get_db)):
    users = db["users"]
    user = users.find_one({"email": email.email})
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")
    
    if not user["verification_status"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You are not a verified registered user. Try to register again with the OTP")

    otp = generate_otp()
    expiry_time = datetime.utcnow() + timedelta(minutes=10)
    
    users.update_one({"_id": user["_id"]}, {"$set": {"reset_token": otp, "reset_expiry": expiry_time}})

    # Generate reset link and send email
    reset_link = f"http://localhost:62168/frontend/reset_password"
    message = MIMEMultipart()
    message["From"] = SENDER_EMAIL
    message["To"] = email.email
    message["Subject"] = "Password Reset Request"
    message_body = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@300..700&family=Playwrite+HR+Lijeva:wght@100..400&display=swap');
            body {{
                font-family: 'Fredoka', sans-serif;
                background: #f0f8ff;
                margin: 0;
                padding: 0;
                color:#000000;
            }}
            .email-container {{
                max-width: 600px;
                margin: 0 auto;
                background: linear-gradient(135deg, #d3d3d3, #f0f8ff);
                border-radius: 10px;
                padding: 30px;
                color: #333;
                box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            }}
            .email-header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .logo-text {{
                font-family: 'Playwrite HR Lijeva', serif;
                background: linear-gradient(to right, #cf23cf, #ff6b08, #f32170);
                font-size: 2rem;
                font-weight: 400;
                color: transparent;
                margin-bottom: 0;
                background-clip: text;
                -webkit-background-clip: text;
            }}
            .otp-box {{
                background: #ffffff;
                border-radius: 8px;
                padding: 20px;
                text-align: center;
                font-size: 1.5rem;
                letter-spacing: 2px;
                font-weight: bold;
                color: #36a69a;
                margin: 20px 0;
            }}
            .button {{
                background-color: #36a69a;
                border-radius: 25px;
                color: #ffffff;
                padding: 15px 30px;
                text-decoration: none;
                font-size: 1rem;
                display: inline-block;
                margin-top: 30px;
            }}
            .button:hover {{
                background-color: #30a08a;
            }}
            .email-body {{
                text-align: center;
            }}
            .email-footer {{
                margin-top: 40px;
                text-align: center;
                font-size: 0.9rem;
                color: #666;
            }}
        </style>
    </head>
    <body>

    <div class="email-container">
        <div class="email-header">
            <span class="logo-text">Insight Edge</span>
        </div>

        <div class="email-body">
            <p>Hello <strong>{user['username']}</strong>,</p>
            <p>You have requested to reset your password. Your one-time OTP is:</p>
            <div class="otp-box">{otp}</div>
            <p>This link will expire in 10 minutes.</p>
            <p>If you did not request a password reset, please ignore this email.</p>
        </div>

        <div class="email-footer">
            <p>Thank you for choosing Insight Edge!</p>
        </div>
    </div>

    </body>
    </html>
    """
    
    message.attach(MIMEText(message_body, "html"))
    
    # Send the email
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, EMAIL_PASSWORD)
        server.sendmail(SENDER_EMAIL, [email.email], message.as_string())
        server.quit()
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        raise HTTPException(status_code=500, detail="Could not send password reset email")

    return {"message": "Password reset link has been sent to your email address"}


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest, db: Collection = Depends(databasem.get_db)):
    request.email = request.email.lower()
    users = db["users"]
    user = users.find_one({"reset_token": request.otp, "email": request.email})
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    if user["reset_expiry"] < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="reset-token has expired")
    # Update the user's password (hash the password in a real application)
    users.update_one(
        {"_id": user["_id"]},
        {"$set": {
            "password": utils.hash(request.new_password),
            "reset_token": None,
            "reset_expiry": None
        }}
    )
    return {"message": "Password has been reset successfully"}

@router.put("/update-username", status_code=status.HTTP_200_OK)
def update_username(
    user_data: schemas.UpdateUsername,  
    db: Collection = Depends(databasem.get_db),  
    current_user: dict = Depends(oauth2.get_current_user)  
):
    users_collection = db["users"]

    try:
        # Fetch the user data from both collections
        user = users_collection.find_one({"_id": current_user["_id"]})
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Check if the user is allowed to change their username
        if user.get("last_username_change"):
            last_change = user["last_username_change"]
            time_diff = datetime.utcnow() - last_change
            if time_diff.days < 15:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, 
                    detail="You can only change your username once every 15 days."
                )

        # Ensure the new username is not already taken
        if users_collection.find_one({"username": user_data.new_username, "verification_status": True}):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail="Username is already taken. Please choose a different one."
            )

        # Update the username in both databases
        users_collection.update_one(
            {"_id": current_user["_id"]},
            {"$set": {"username": user_data.new_username, "last_username_change": datetime.utcnow()}}
        )

        logging.info(f"Username updated successfully for user ID {current_user['_id']}")
        return {"message": "Username updated successfully", "new_username": user_data.new_username}

    except Exception as e:
        logger.error(f"An error occurred while updating the username: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while updating the username.")

@router.put("/update-name", status_code=status.HTTP_200_OK)
def update_name(
    user_data: schemas.UpdateName,
    db: Collection = Depends(databasem.get_db),
    current_user: dict = Depends(oauth2.get_current_user)
):
    users_collection = db["users"]

    try:
        # Fetch the user data from both collections
        user = users_collection.find_one({"_id": current_user["_id"]})
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Update the name in both databases
        users_collection.update_one(
            {"_id": current_user["_id"]},
            {"$set": {"firstname": user_data.first_name, "lastname": user_data.last_name}}
        )

        logging.info(f"Name updated successfully for user ID {current_user['_id']}")
        return {
            "message": "Name updated successfully",
            "new_first_name": user_data.first_name,
            "new_last_name": user_data.last_name
        }

    except Exception as e:
        logger.error(f"An error occurred while updating the name: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while updating the name.")


@router.post("/auth/social-signup")
async def social_signup(
    user_data: dict,
    db: Collection = Depends(databasem.get_db),
):
    try:
        users_collection = db["users"]
        events_collection = db["events"]
        
        user_data['email'] = user_data['email'].lower()
        
        # Check existing users in primary database
        existing_user = users_collection.find_one({"email": user_data['email']})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email {user_data['email']} has already been used"
            )
            
        if users_collection.find_one({"username": user_data['username']}) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Username {user_data['username']} has already been used"
            )
            
        hashed_password = utils.hash(user_data['password'])
        
        new_user = {
            "firstname": user_data['firstname'],
            "lastname": user_data['lastname'],
            "username": user_data['username'],
            "email": user_data['email'],
            "public_profile": True,
            "password": hashed_password,
            "created_at": datetime.utcnow(),
            "verification_status": True, 
        }
        
        # Add auth provider specific data
        if 'google_id' in user_data:
            new_user['google_id'] = user_data['google_id']
            new_user['auth_provider'] = 'google'
            if 'profile_photo' in user_data:
                new_user['profile_photo'] = user_data['profile_photo']

        # Insert into primary database
        result=users_collection.insert_one(new_user)
        created_user = users_collection.find_one({"email": user_data['email']})
    
        
        # Log registration event
        Event = {
            "event_type": "User_registration",
            "user_id": str(created_user["_id"]),
            "timestamp": datetime.utcnow(),
            "registration_type": "social",
            "provider": new_user.get('auth_provider', 'unknown')
        }
        events_collection.insert_one(Event)
        

        access_token = oauth2.create_access_token(data={"sub": str(created_user["_id"])})
        refresh_token = oauth2.create_refresh_token(data={"sub": str(created_user["_id"])})
        
        # Store refresh token
        db["refresh_tokens"].insert_one({
            "user_id": str(created_user["_id"]),
            "refresh_token": refresh_token,
            "created_at": datetime.utcnow()
        })

        # Create response with all tokens and user data
        response = JSONResponse(
            content={
                "message": f"{created_user['username']} registered successfully",
                "user": {
                    "id": str(created_user["_id"]),
                    "firstname": str(created_user['firstname']),
                    "lastname": str(created_user['lastname']),
                    "username": created_user["username"],
                    "email": created_user["email"],
                    "created_at": created_user["created_at"].isoformat() if created_user.get("created_at") else None,
                    "auth_provider": created_user.get("auth_provider"),
                    "profile_photo": created_user.get("profile_photo")
                },
                "tokens": {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_type": "Bearer"
                }
            }
        )
        
        response.set_cookie(key="access_token", value=access_token)
        
        # Add welcome email for first-time login
        existing_login = events_collection.find_one({
            "user_id": str(created_user["_id"]), 
            "event_type": "Login"
        })
        
        if not existing_login:
            try:
                send_welcome_email(created_user['email'], created_user['username'])
            except Exception as e:
                logger.error(f"Could not send welcome email: {e}")
                
        # Log login event
        event_result = {
            "event_type": "Login",
            "user_id": str(created_user["_id"]),
            "timestamp": datetime.utcnow(),
            "registration_type": "social",
            "provider": created_user.get('auth_provider', 'unknown')
        }
        events_collection.insert_one(event_result)
        
        return response
        
    except Exception as e:
        logger.error(f"An error occurred in social_signup: {e}")
        raise HTTPException(status_code=500, detail=str(e))