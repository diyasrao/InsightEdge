from passlib.context import CryptContext
from pydantic import BaseModel

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash(password: str):
    return pwd_context.hash(password)


def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Function to generate a random OTP
def generate_otp():
  import random
  digits = "0123456789"
  return "".join(random.choice(digits) for _ in range(6))

  