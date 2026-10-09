import os
import numpy as np

model = None
TF_AVAILABLE = False

try:
    from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input
    from tensorflow.keras.preprocessing import image
    from tensorflow.keras.models import Model
    
    # Load CNN model (MobileNetV2 as feature extractor)
    try:
        base_model = MobileNetV2(weights='imagenet', include_top=False, pooling='avg')
        model = Model(inputs=base_model.input, outputs=base_model.output)
        TF_AVAILABLE = True
        print("[OK] TensorFlow MobileNetV2 model loaded successfully")
    except Exception as model_error:
        print(f"[WARN] Could not load MobileNetV2 model: {model_error}")
        print("Falling back to mock embeddings for testing")
        TF_AVAILABLE = False
        
except ImportError as import_error:
    print(f"[WARN] TensorFlow import failed: {import_error}")
    print("Falling back to mock embeddings for testing")
    TF_AVAILABLE = False
except Exception as e:
    print(f"[WARN] Unexpected error loading TensorFlow: {e}")
    print("Falling back to mock embeddings for testing")
    TF_AVAILABLE = False

def get_embedding(img_path):
    """Extract face embedding using pretrained MobileNetV2 CNN"""
    if not TF_AVAILABLE or model is None:
        # Return mock embedding for demonstration/testing
        print(f"Using mock embedding for: {img_path}")
        return np.random.rand(1280)
    
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    embedding = model.predict(img_array)
    return embedding.flatten()

def compare_faces(embedding1, embedding2, threshold=0.6):
    """Compare two face embeddings using Euclidean distance"""
    distance = np.linalg.norm(embedding1 - embedding2)
    return distance < threshold

