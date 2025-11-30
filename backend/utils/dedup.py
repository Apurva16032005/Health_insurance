import imagehash
from PIL import Image
import os
import pickle

# Database simulation (In prod, use Redis/SQL)
DB_PATH = "data/phash_database.pkl"

def load_db():
    if os.path.exists(DB_PATH):
        with open(DB_PATH, "rb") as f:
            return pickle.load(f)
    return {}

def save_db(db):
    os.makedirs("data", exist_ok=True)
    with open(DB_PATH, "wb") as f:
        pickle.dump(db, f)

def check_duplicate(image_path, claim_id):
    """
    Checks if this image (or a similar one) has been submitted before.
    """
    db = load_db()
    
    img = Image.open(image_path)
    current_hash = imagehash.phash(img)
    
    # Check against all stored hashes
    for stored_id, stored_hash in db.items():
        # Hamming distance: 0 = exact match, < 5 = very similar (cropped/resized)
        if current_hash - stored_hash < 5:
            return {
                "is_duplicate": True,
                "original_claim_id": stored_id,
                "message": f"Duplicate of Claim {stored_id}"
            }
    
    # If unique, add to DB
    db[claim_id] = current_hash
    save_db(db)
    
    return {"is_duplicate": False}