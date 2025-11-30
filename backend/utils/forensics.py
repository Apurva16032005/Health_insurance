import cv2
import numpy as np
from PIL import Image, ExifTags
import os

def check_metadata(image_path):
    """
    Checks EXIF data for editing software signatures.
    """
    try:
        img = Image.open(image_path)
        exif = img._getexif()
        if not exif:
            return {"has_metadata": False, "software": None}

        # Map Exif tags to names
        exif_data = {ExifTags.TAGS.get(k, k): v for k, v in exif.items()}
        
        software = exif_data.get("Software", "Unknown")
        date_time = exif_data.get("DateTime", "Unknown")
        
        suspicious_tools = ["Photoshop", "GIMP", "Canva", "Paint"]
        is_suspicious = any(tool.lower() in str(software).lower() for tool in suspicious_tools)
        
        return {
            "has_metadata": True,
            "software": software,
            "date": date_time,
            "is_suspicious": is_suspicious
        }
    except Exception as e:
        return {"error": str(e)}

def error_level_analysis(image_path, quality=90):
    """
    Computes Error Level Analysis (ELA) score.
    Higher ELA difference means higher likelihood of manipulation.
    """
    original = cv2.imread(image_path)
    
    # Compress and reload
    temp_path = "temp_ela_check.jpg"
    cv2.imwrite(temp_path, original, [cv2.IMWRITE_JPEG_QUALITY, quality])
    compressed = cv2.imread(temp_path)
    os.remove(temp_path)
    
    # Calculate difference
    diff = cv2.absdiff(original, compressed)
    
    # Calculate the average intensity of the noise
    # If the image was spliced, the noise levels will be inconsistent
    score = np.mean(diff)
    
    # Normalize score roughly 0-1 (Empirical threshold)
    normalized_score = min(score / 10.0, 1.0)
    
    return normalized_score