import cv2
import numpy as np
from PIL import Image

def preprocess_for_ocr(image_path):
    """
    Cleans image to improve OCR accuracy.
    - Grayscale
    - Adaptive Thresholding (removes shadows/lighting issues)
    - Denoising
    """
    img = cv2.imread(image_path)
    
    # 1. Convert to Grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 2. Remove Noise (salt-and-pepper noise from scanning)
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    
    # 3. Adaptive Thresholding (Binarization)
    # This creates a crisp black-and-white image, great for text extraction
    binary = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    
    # Save a temp file for debugging/OCR
    temp_path = image_path.replace(".", "_clean.")
    cv2.imwrite(temp_path, binary)
    
    return temp_path