import firebase_admin
from firebase_admin import credentials, firestore

# Path to your Firebase Admin SDK key file
cred = credentials.Certificate("firebase-key.json")

# Initialize the Firebase Admin SDK
firebase_admin.initialize_app(cred)

# Get Firestore client
db = firestore.client()
