import os
import cv2
import numpy as np

_face_app = None


def _get_face_app():
    global _face_app
    if _face_app is None:
        from insightface.app import FaceAnalysis

        model_name = os.getenv("INSIGHTFACE_MODEL", "buffalo_l")
        print(f"[INFO] Loading InsightFace model '{model_name}' on CPU")
        print("[NOTICE] Verify the selected model's license before deployment.")
        _face_app = FaceAnalysis(name=model_name, providers=["CPUExecutionProvider"])
        _face_app.prepare(ctx_id=-1, det_size=(640, 640))
    return _face_app


def initialize_face_engine():
    """Load InsightFace before the API starts accepting recognition requests."""
    _get_face_app()


def get_embedding(img_path):
    """Extract a normalized InsightFace embedding from an image file."""
    image = cv2.imread(img_path)
    if image is None:
        raise ValueError(f"Could not read image: {img_path}")

    faces = _get_face_app().get(image)
    if not faces:
        raise ValueError("No face detected in image")

    face = max(faces, key=lambda detected: detected.bbox[2] * detected.bbox[3])
    embedding = np.asarray(face.normed_embedding, dtype=np.float32).reshape(-1)
    norm = np.linalg.norm(embedding)
    if norm == 0:
        raise ValueError("InsightFace returned an empty embedding")
    return embedding / norm


def cosine_similarity(embedding1, embedding2):
    """Return cosine similarity, or -1 for incompatible/invalid vectors."""
    first = np.asarray(embedding1, dtype=np.float32).reshape(-1)
    second = np.asarray(embedding2, dtype=np.float32).reshape(-1)
    if first.shape != second.shape or first.size == 0:
        return -1.0

    first_norm = np.linalg.norm(first)
    second_norm = np.linalg.norm(second)
    if first_norm == 0 or second_norm == 0:
        return -1.0
    return float(np.dot(first, second) / (first_norm * second_norm))


def compare_faces(embedding1, embedding2, threshold=0.4):
    """Compare normalized embeddings using a maximum cosine-distance threshold."""
    return 1.0 - cosine_similarity(embedding1, embedding2) < threshold
