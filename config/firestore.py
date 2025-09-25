import firebase_admin
from firebase_admin import credentials, firestore
from os import getenv
from pathlib import Path
from utils.exceptions import FirestoreCredentialError

credential_filename = getenv('FIREBASE_CREDENTIAL', None)
firestore_cred_path = Path(f'./credentials/{credential_filename}')
if not firestore_cred_path.exists():
    raise FirestoreCredentialError("Firebase credential file not found", filename=str(firestore_cred_path))
cred = credentials.Certificate(f'./credentials/{credential_filename}')
app = firebase_admin.initialize_app(cred)
db = firestore.client()