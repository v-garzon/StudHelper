import firebase_admin
from firebase_admin import credentials, auth
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

# Initialize Firebase Admin SDK
def initialize_firebase():
    """Initialize Firebase Admin SDK with service account credentials"""
    try:
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred, {
            'projectId': settings.FIREBASE_PROJECT_ID
        })
        logger.info("Firebase Admin SDK initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")
        raise

def verify_firebase_token(id_token: str) -> dict:
    """
    Verify Firebase ID token and return decoded token
    
    Args:
        id_token: Firebase ID token from client
    
    Returns:
        dict with:
            - uid: Firebase user ID
            - email: User email
            - email_verified: Boolean
            - name: Display name (if available)
            - firebase: Provider information
    
    Raises:
        ValueError: If token is invalid or expired
    """
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except auth.InvalidIdTokenError:
        raise ValueError("Invalid Firebase token")
    except auth.ExpiredIdTokenError:
        raise ValueError("Firebase token expired")
    except Exception as e:
        logger.error(f"Firebase token verification error: {e}")
        raise ValueError("Token verification failed")


