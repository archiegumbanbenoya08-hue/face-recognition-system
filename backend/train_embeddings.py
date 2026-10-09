#!/usr/bin/env python3
"""
Scan student image folders and dataset, generate face embeddings using
`encoding.FaceEncoder`, and save results to `encodings.json` and
`trained_faces.pkl` for compatibility with simpler scripts.

Usage:
    python train_embeddings.py

Output:
 - encodings.json  : mapping image_path -> encoding (list)
 - trained_faces.pkl : dict with "encodings" (list of arrays) and "names" (list)
"""

import os
import json
import pickle
from typing import Dict, List
import numpy as np

from encoding import FaceEncoder, EncodingStorage

ROOT = os.path.dirname(__file__)
STUDENT_IMAGES = os.path.join(ROOT, "student_images")
DATASET_DIR = os.path.join(ROOT, "dataset")
OUT_JSON = os.path.join(ROOT, "encodings.json")
OUT_PKL = os.path.join(ROOT, "trained_faces.pkl")


def gather_image_paths() -> Dict[str, List[str]]:
    """Return mapping key -> list of image paths.

    - For `student_images/`: uses filename (without ext) as key (student_id)
    - For `dataset/`: uses subfolder name as key
    """
    result = {}

    # student_images: files named like <student_id>.jpg
    if os.path.isdir(STUDENT_IMAGES):
        for fname in sorted(os.listdir(STUDENT_IMAGES)):
            if fname.lower().endswith((".jpg", ".jpeg", ".png")):
                key = os.path.splitext(fname)[0]
                path = os.path.join(STUDENT_IMAGES, fname)
                result.setdefault(key, []).append(path)

    # dataset: folders per person
    if os.path.isdir(DATASET_DIR):
        for person in sorted(os.listdir(DATASET_DIR)):
            person_folder = os.path.join(DATASET_DIR, person)
            if not os.path.isdir(person_folder):
                continue
            for fname in sorted(os.listdir(person_folder)):
                if fname.lower().endswith((".jpg", ".jpeg", ".png")):
                    path = os.path.join(person_folder, fname)
                    result.setdefault(person, []).append(path)

    return result


def main():
    images_map = gather_image_paths()
    if not images_map:
        print("No images found in student_images/ or dataset/. Nothing to train.")
        return

    encodings_map = {}
    pkl_encodings = []
    pkl_names = []

    total = sum(len(v) for v in images_map.values())
    processed = 0

    print(f"Found {len(images_map)} identities and {total} images. Encoding...")

    for name, paths in images_map.items():
        for p in paths:
            processed += 1
            try:
                encoding = FaceEncoder.encode_face(p)
                if encoding is None:
                    print(f"  [SKIP] No face in {p}")
                    continue

                # Save per-image encoding for lookup
                encodings_map[p] = encoding.tolist()

                # Also add to pkl lists (one encoding per entry)
                pkl_encodings.append(encoding)
                pkl_names.append(name)

                print(f"  [{processed}/{total}] Encoded {p} -> {name}")
            except Exception as e:
                print(f"  [ERROR] {p}: {e}")

    # Save encodings JSON
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(encodings_map, f, indent=2)
    print(f"Saved encodings JSON: {OUT_JSON}")

    # Save pickle in legacy format
    # convert numpy arrays to lists for pickle compatibility
    try:
        data = {"encodings": [np.asarray(x).tolist() for x in pkl_encodings], "names": pkl_names}
        with open(OUT_PKL, "wb") as f:
            pickle.dump(data, f)
        print(f"Saved legacy trained faces pickle: {OUT_PKL}")
    except Exception as e:
        print(f"Could not save pickle: {e}")


if __name__ == "__main__":
    main()
