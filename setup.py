from deepface import DeepFace
from constants import MODEL_NAME

DeepFace.build_model(model_name=MODEL_NAME, task='facial_recognition')
DeepFace.build_model(task="spoofing", model_name="Fasnet")