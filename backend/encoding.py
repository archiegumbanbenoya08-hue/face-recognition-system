#!/usr/bin/env python3
"""
Face encoding module for generating and managing face embeddings.
"""

import numpy as np
import json
from typing import List, Dict, Optional
import os
from face_engine import cosine_similarity, get_embedding


class FaceEncoder:
    """Generate face encodings from images"""
    
    @staticmethod
    def encode_face(image_path: str, use_fr: bool = True) -> Optional[np.ndarray]:
        """
        Generate face encoding from image file.
        
        Args:
            image_path: Path to image file
            use_fr: Prefer face_recognition library if available
        
        Returns:
            Face encoding vector or None if no face found
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        try:
            return get_embedding(image_path)
        except ValueError as error:
            if str(error) == "No face detected in image":
                return None
            raise
    
    @staticmethod
    def encode_batch(image_paths: List[str]) -> Dict[str, np.ndarray]:
        """
        Generate encodings for multiple images.
        
        Args:
            image_paths: List of image file paths
        
        Returns:
            Dictionary mapping image path to encoding
        """
        encodings = {}
        
        for i, img_path in enumerate(image_paths):
            try:
                encoding = FaceEncoder.encode_face(img_path)
                if encoding is not None:
                    encodings[img_path] = encoding
                    print(f"  [{i+1}/{len(image_paths)}] Encoded: {os.path.basename(img_path)}")
                else:
                    print(f"  [{i+1}/{len(image_paths)}] Skipped (no face): {os.path.basename(img_path)}")
            except Exception as e:
                print(f"  [{i+1}/{len(image_paths)}] Error: {os.path.basename(img_path)} - {e}")
        
        return encodings


class EncodingStorage:
    """Store and retrieve face encodings in JSON format"""
    
    @staticmethod
    def save_encoding(encoding: np.ndarray) -> str:
        """
        Convert encoding to JSON-serializable format.
        
        Args:
            encoding: Numpy array
        
        Returns:
            JSON string
        """
        return json.dumps(encoding.tolist())
    
    @staticmethod
    def load_encoding(encoding_json: str) -> np.ndarray:
        """
        Load encoding from JSON format.
        
        Args:
            encoding_json: JSON string
        
        Returns:
            Numpy array
        """
        return np.array(json.loads(encoding_json))
    
    @staticmethod
    def save_encodings_to_file(
        encodings: Dict[str, np.ndarray],
        output_file: str
    ) -> None:
        """
        Save multiple encodings to JSON file.
        
        Args:
            encodings: Dictionary of encodings
            output_file: Output file path
        """
        data = {
            path: encoding.tolist()
            for path, encoding in encodings.items()
        }
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✓ Saved {len(encodings)} encodings to {output_file}")
    
    @staticmethod
    def load_encodings_from_file(input_file: str) -> Dict[str, np.ndarray]:
        """
        Load encodings from JSON file.
        
        Args:
            input_file: Input file path
        
        Returns:
            Dictionary of encodings
        """
        with open(input_file, 'r') as f:
            data = json.load(f)
        
        return {
            path: np.array(encoding)
            for path, encoding in data.items()
        }


class FaceComparison:
    """Compare face encodings"""
    
    @staticmethod
    def distance(encoding1: np.ndarray, encoding2: np.ndarray) -> float:
        """
        Calculate cosine distance between normalized face embeddings.
        
        Args:
            encoding1: First face encoding
            encoding2: Second face encoding
        
        Returns:
            Distance value
        """
        return 1.0 - cosine_similarity(encoding1, encoding2)
    
    @staticmethod
    def similarity(encoding1: np.ndarray, encoding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between encodings.
        
        Args:
            encoding1: First face encoding
            encoding2: Second face encoding
        
        Returns:
            Similarity score (0-1)
        """
        return cosine_similarity(encoding1, encoding2)
    
    @staticmethod
    def compare_faces(
        encoding1: np.ndarray,
        encoding2: np.ndarray,
        distance_threshold: float = 0.4
    ) -> bool:
        """
        Compare two face encodings.
        
        Args:
            encoding1: First face encoding
            encoding2: Second face encoding
            distance_threshold: Maximum distance for match
        
        Returns:
            True if faces match, False otherwise
        """
        distance = FaceComparison.distance(encoding1, encoding2)
        return distance < distance_threshold
    
    @staticmethod
    def find_best_match(
        query_encoding: np.ndarray,
        reference_encodings: Dict[str, np.ndarray],
        distance_threshold: float = 0.4
    ) -> Optional[tuple]:
        """
        Find best matching face in references.
        
        Args:
            query_encoding: Query face encoding
            reference_encodings: Dictionary of reference encodings
            distance_threshold: Maximum distance for match
        
        Returns:
            Tuple of (key, distance) or None if no match
        """
        best_key = None
        best_distance = float('inf')
        
        for key, ref_encoding in reference_encodings.items():
            dist = FaceComparison.distance(query_encoding, ref_encoding)
            if dist < best_distance:
                best_distance = dist
                best_key = key
        
        if best_distance < distance_threshold:
            return (best_key, best_distance)
        
        return None


if __name__ == "__main__":
    print("\n" + "="*50)
    print("FACE ENCODING MODULE TEST")
    print("="*50 + "\n")
    
    # Test encoding generation
    print("Testing encoding generation...")
    print("InsightFace is loaded on the first encoding request.")
    
    # Test encoding serialization
    test_encoding = np.random.rand(128)
    json_str = EncodingStorage.save_encoding(test_encoding)
    loaded_encoding = EncodingStorage.load_encoding(json_str)
    
    if np.allclose(test_encoding, loaded_encoding):
        print("✓ Encoding serialization works")
    else:
        print("✗ Encoding serialization failed")
    
    # Test comparison
    encoding1 = np.random.rand(128)
    encoding2 = encoding1.copy()
    encoding3 = np.random.rand(128)
    
    dist_same = FaceComparison.distance(encoding1, encoding2)
    dist_different = FaceComparison.distance(encoding1, encoding3)
    
    print(f"✓ Distance same face: {dist_same:.4f}")
    print(f"✓ Distance different face: {dist_different:.4f}")
