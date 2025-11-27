import os
import firebase_admin
from firebase_admin import auth, credentials

# Path to service account JSON
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
SERVICE_ACCOUNT = os.path.join(BASE_DIR, "serviceAccountKey.json")

# --- Initialize Firebase (only once) ---
def init_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate(SERVICE_ACCOUNT)
        firebase_admin.initialize_app(cred)

# --- Token verification ---
def verify_firebase_token(token: str):
    if not firebase_admin._apps:
        init_firebase()

    decoded = auth.verify_id_token(token)
    return decoded
