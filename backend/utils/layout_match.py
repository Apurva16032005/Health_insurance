import cv2
import os

TEMPLATE_DIR = "backend/uploads/templates/hospitals/"

def match_template(image_path, hospital_name):
    """
    Compares uploaded image features with the specific hospital's master template.
    """
    # Normalize hospital name to filename (e.g., "Apollo Hospital" -> "apollo.jpg")
    template_filename = hospital_name.lower().replace(" ", "_") + ".jpg"
    template_path = os.path.join(TEMPLATE_DIR, template_filename)
    
    if not os.path.exists(template_path):
        return {"match_score": 0.5, "status": "No template found for this hospital"}
    
    # Load images
    img1 = cv2.imread(template_path, 0) # Master Template
    img2 = cv2.imread(image_path, 0)    # Uploaded User Bill
    
    # Initialize ORB detector (Faster than SIFT for web apps)
    orb = cv2.ORB_create()
    
    # Find keypoints and descriptors
    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)
    
    if des1 is None or des2 is None:
        return {"match_score": 0.0, "status": "Failed to extract features"}

    # Match features
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)
    
    # Sort matches by distance (best matches first)
    matches = sorted(matches, key = lambda x:x.distance)
    
    # Calculate score based on number of good matches
    good_matches = len([m for m in matches if m.distance < 50])
    score = min(good_matches / 50.0, 1.0) # Normalize
    
    return {
        "match_score": round(score, 2),
        "status": "Match Found" if score > 0.4 else "Layout Mismatch"
    }