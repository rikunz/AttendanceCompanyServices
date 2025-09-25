from logging_config import logger
from logging_config import setup_logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from nodes.firestore_client import FirestoreClient
from utils.exceptions import *
from deepface import DeepFace
from constants import *
import io
from deepface.modules.verification import find_distance

setup_logging()

app = Flask(__name__)
CORS(app)
firestore_client = FirestoreClient()
    
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200

@app.route('/api/docs/<path:path>', methods=['GET'])
def serve_documentation(path):
    try:
        return send_from_directory('docs', path)
    except Exception as e:
        logger.error(f"Error serving documentation file {path}: {e}")
        return jsonify({"error": "File not found."}), 404


@app.route('/api/users/face-embedding', methods=['GET'])
def get_face_embedding_user():
    try:
        session_cookie = request.cookies.get('__session', None)
        if not session_cookie:
            return jsonify({"error": "Session cookie is missing."}), 401
        uid = firestore_client.get_uid_from_session(session_cookie)
        if not uid:
            return jsonify({"error": "Invalid session."}), 401
        face_embedding = firestore_client.get_user_face_embedding(uid)
        return jsonify({"error": False, "face_embedding": face_embedding}), 200
    except RetrieveDBError as e:
        logger.error(f"Error retrieving user data with session cookie: {session_cookie}")
        return jsonify({"error": True, "message": "Error retrieving user data."}), 500
    except InvalidSessionError as e:
        logger.error(f"Invalid session with session cookie: {session_cookie}")
        return jsonify({"error": True, "message": "Invalid session."}), 401
    except APIError as e:
        logger.error(f"Error retrieving user face embedding with session cookie: {session_cookie}")
        return jsonify({"error": True, "message": "Error retrieving user face embedding."}), 401
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({"error": True, "message": "An unexpected error occurred."}), 500

@app.route('/api/users/face-embedding', methods=['POST'])
def upsert_face_embedding_user():
    try:
        session_cookie = request.cookies.get('__session', None)
        if not session_cookie:
            return jsonify({"error": "Session cookie is missing."}), 401
        uid = firestore_client.get_uid_from_session(session_cookie)
        logger.info(f"Processing upsert user with UID: {uid}")
        if not uid:
            return jsonify({"error": "Invalid session."}), 401
        if 'face_image' not in request.files:
            logger.warning("Face image is missing in the request.")
            return jsonify({"error": "Face image is missing."}), 400
        face_image = request.files['face_image']
        if not face_image.content_type.startswith('image/'):
            logger.warning("Uploaded file is not an image.")
            return jsonify({"error": "File must be an image."}), 400
        face_embeddings = DeepFace.represent(io.BytesIO(face_image.read()), detector_backend=BACKEND_DEEPFACE, max_faces=2, model_name=MODEL_NAME, anti_spoofing=True)
        if not face_embeddings or len(face_embeddings) == 0:
            logger.warning("No face detected in the provided image.")
            return jsonify({"error": "No face detected in the image."}), 400
        if len(face_embeddings) > 1:
            logger.warning("Multiple faces detected in the provided image.")
            return jsonify({"error": "Multiple faces detected in the image."}), 400
        face_embedding = face_embeddings[0].get('embedding', [])
        if not face_embedding or len(face_embedding) == 0:
            logger.warning("Failed to extract face embedding from the image.")
            return jsonify({"error": "Failed to extract face embedding."}), 500
        firestore_client.upsert_user_face_embedding(uid, face_embedding)
        return jsonify({"error": False, "message": "Face embedding upserted successfully."}), 200
    except RetrieveDBError as e:
        logger.error(f"Error retrieving user data with session cookie: {session_cookie}")
        return jsonify({"error": True, "message": "Error retrieving user data."}), 500
    except UpdateDBError as e:
        logger.error(f"Error updating user face embedding with session cookie: {session_cookie}")
        return jsonify({"error": True, "message": "Error updating user face embedding."}), 500
    except APIError as e:
        logger.error(f"Error upserting user face embedding with session cookie: {session_cookie}")
        return jsonify({"error": True, "message": "Error upserting user face embedding."}), 500
    except Exception as e:
        if str(e) == "Spoof detected in the given image.":
            return jsonify({"error": True, "message": "Spoof detected in the given image."}), 400
        logger.error(f"Unexpected error: {e}")
        return jsonify({"error": True, "message": "An unexpected error occurred."}), 500
    
@app.route('/api/users/verify-face', methods=['POST'])
def verify_face_user():
    try:
        session_cookie = request.cookies.get('__session', None)
        if not session_cookie:
            return jsonify({"error": "Session cookie is missing."}), 401
        uid = firestore_client.get_uid_from_session(session_cookie)
        if not uid:
            return jsonify({"error": "Invalid session."}), 401
        logger.info(f"Retrieving user_id: {uid}")
        if 'face_image' not in request.files:
            return jsonify({"error": "Face image is missing."}), 400
        stored_face_embedding = firestore_client.get_user_face_embedding(uid)
        if not stored_face_embedding or len(stored_face_embedding) == 0:
            return jsonify({"error": "No face embedding found for the user."}), 404
        face_image = request.files['face_image']
        if not face_image.content_type.startswith('image/'):
            return jsonify({"error": "File must be an image."}), 400
        DeepFace.verify
        face_embeddings = DeepFace.represent(io.BytesIO(face_image.read()), detector_backend=BACKEND_DEEPFACE, model_name=MODEL_NAME, anti_spoofing=True)
        if not face_embeddings or len(face_embeddings) == 0:
            return jsonify({"error": "No face detected in the image."}), 400
        if len(face_embeddings) > 1:
            return jsonify({"error": "Multiple faces detected in the image."}), 400
        
        current_face_embedding = face_embeddings[0]['embedding']
        if not current_face_embedding or len(current_face_embedding) == 0:
            return jsonify({"error": "Failed to extract face embedding."}), 500
        distance = find_distance(current_face_embedding, stored_face_embedding, distance_metric=DISTANCE_METRIC)
        pretuned_threshold = DeepFace.verification.find_threshold(MODEL_NAME, DISTANCE_METRIC)
        is_verified = distance < pretuned_threshold
        confidence = DeepFace.verification.find_confidence(
            distance=distance,
            model_name=MODEL_NAME,
            distance_metric=DISTANCE_METRIC,
            verified=is_verified,
        )
        detail_info = {"threshold": pretuned_threshold, 'distance': distance, 'confidence': confidence}
        return jsonify({"error": False, "verified": bool(is_verified), "detail": detail_info}), 200
    except APIError as e:
        logger.error(f"Error verifying user face embedding with session cookie: {session_cookie}")
        return jsonify({"error": True, "message": "Error verifying user face embedding."}), 500
    except RetrieveDBError as e:
        logger.error(f"Error retrieving user data with session cookie: {session_cookie}")
        return jsonify({"error": True, "message": "Error retrieving user data."}), 500
    except InvalidSessionError as e:
        logger.error(f"Invalid session with session cookie: {session_cookie}")
        return jsonify({"error": True, "message": "Invalid session."}), 401
    except Exception as e:
        if str(e) == "Spoof detected in the given image.":
            return jsonify({"error": True, "message": "Spoof detected in the given image."}), 400
        logger.error(f"Unexpected error: {e}")
        return jsonify({"error": True, "message": "An unexpected error occurred."}), 500