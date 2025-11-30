import exifread
from PIL import Image
from PIL.ExifTags import TAGS
import os

def extract_metadata(image_path):
    """
    Extracts EXIF and XMP metadata from the image.
    Returns a dictionary of suspicious flags and raw data.
    """
    metadata = {
        "has_exif": False,
        "software_used": "Unknown",
        "camera_model": "Unknown",
        "original_date": None,
        "is_suspicious": False,
        "flags": []
    }

    try:
        # 1. Open file with specialized EXIF library
        with open(image_path, 'rb') as f:
            tags = exifread.process_file(f, details=False)
        
        if not tags:
            return metadata
        
        metadata["has_exif"] = True
        
        # 2. Extract Key Fields
        if 'Image Software' in tags:
            metadata["software_used"] = str(tags['Image Software'])
        
        if 'Image Model' in tags:
            metadata["camera_model"] = str(tags['Image Model'])
            
        if 'EXIF DateTimeOriginal' in tags:
            metadata["original_date"] = str(tags['EXIF DateTimeOriginal'])

        # 3. Security Checks (The "Trap")
        
        # Check for editing software
        suspicious_tools = ["Adobe", "Photoshop", "GIMP", "Editor", "Canva", "Picasa"]
        for tool in suspicious_tools:
            if tool.lower() in metadata["software_used"].lower():
                metadata["is_suspicious"] = True
                metadata["flags"].append(f"Edited with {metadata['software_used']}")

        # Check for Device Mismatch (e.g., Image says 'iPhone' but resolution is weird)
        # (Advanced logic can be added here)

    except Exception as e:
        print(f"Error extracting metadata: {e}")

    return metadata