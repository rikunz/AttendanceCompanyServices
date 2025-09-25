from config.firestore import db
from utils.exceptions import RetrieveDBError, UpdateDBError, InvalidSessionError
from google.cloud.firestore_v1.vector import Vector
from firebase_admin import auth
from logging_config import logger

class FirestoreClient:
    def __init__(self):
        """Initialize Firestore client."""
        self.db = db

    def get_user_face_embedding(self, user_id):
        """Get a user's face embedding by user ID."""
        if not self.db.collection("users").document(user_id).get().exists:
            logger.warning(f"User {user_id} does not exist in Firestore.")
            raise RetrieveDBError(f"User {user_id} does not exist in Firestore.", filename=__file__)
        face_embedding = self.db.collection("users").document(user_id).get(['face_embedding'])
        if not face_embedding.exists or 'face_embedding' not in face_embedding.to_dict():
            logger.warning(f"Face embedding for user {user_id} does not exist.")
            raise RetrieveDBError(f"Face embedding for user {user_id} does not exist.", filename=__file__)
        return face_embedding.to_dict().get('face_embedding')
    
    def upsert_user_face_embedding(self, user_id:str, face_embedding: Vector):
        """Upsert a user's face embedding by user ID."""
        try:
            doc_ref = self.db.collection("users").document(user_id)
            doc_ref.set({
                "face_embedding": Vector(face_embedding)
            }, merge=True)
        except Exception as e:
            logger.error(f"Error updating face embedding for user {user_id}: {e}")
            raise UpdateDBError(f"Error updating face embedding for user {user_id}: {e}", filename=__file__)
        
    def get_uid_from_session(self, session_string:str):
        """Verify session cookie and return UID."""
        try:
            decoded_session = auth.verify_session_cookie(session_string, True)
            if not decoded_session or 'uid' not in decoded_session:
                logger.warning("Invalid session cookie: UID not found.")
                raise InvalidSessionError("Invalid session cookie: UID not found.", filename=__file__)
            return decoded_session['uid']
        except Exception as e:
            logger.error(f"Error verifying session cookie: {e}")
            return None
