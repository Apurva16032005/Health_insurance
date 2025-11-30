import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import numpy as np
import cv2
import os

# Define the standard transformation for the CNN
TRANSFORMS = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

class ForgeryDetectionModel:
    def __init__(self, model_path=None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"🔹 Loading CNN Model on {self.device}...")
        
        # Load a pre-trained EfficientNet (Robust feature extractor)
        self.model = models.efficientnet_b0(pretrained=True)
        
        # Replace the classifier head for Binary Classification (Real vs Fake)
        self.model.classifier[1] = nn.Linear(self.model.classifier[1].in_features, 1)
        self.model = self.model.to(self.device)
        self.model.eval()

        # If you have a custom trained .pth file, load it here
        if model_path and os.path.exists(model_path):
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
            print("✅ Custom Forgery weights loaded.")

    def preprocess_image(self, image_path):
        """Converts image to tensor for model input"""
        image = Image.open(image_path).convert('RGB')
        return TRANSFORMS(image).unsqueeze(0).to(self.device), image

    def detect_forgery(self, image_path, output_folder="reports/"):
        """
        Main function to predict tampering score and generate Grad-CAM heatmap.
        Returns: { 'score': float, 'heatmap_path': str }
        """
        input_tensor, original_image = self.preprocess_image(image_path)
        
        # 1. Prediction
        with torch.no_grad():
            output = self.model(input_tensor)
            prob = torch.sigmoid(output).item()  # Score 0 (Real) to 1 (Fake)

        # 2. Generate Grad-CAM Heatmap (Simplified for Inference)
        # Note: For full Grad-CAM, we usually hook gradients. 
        # Here we simulate a heatmap for demo purposes using the activation layer.
        # In a real training loop, you would use the 'grad-cam' library.
        
        heatmap_path = self.generate_heatmap_overlay(original_image, prob, output_folder, image_path)

        return {
            "score": round(prob, 4),
            "is_tampered": prob > 0.5,
            "heatmap_path": heatmap_path
        }

    def generate_heatmap_overlay(self, original_image, score, output_folder, original_path):
        """
        Generates a visual overlay.
        If score is high, highlights regions (simulated here with Noise Analysis for the MVP).
        """
        # Convert PIL to OpenCV
        img_cv = cv2.cvtColor(np.array(original_image), cv2.COLOR_RGB2BGR)
        
        if score > 0.5:
            # PERFORM ERROR LEVEL ANALYSIS (ELA) VISUALIZATION
            # This reveals hidden compression artifacts (Photoshop traces)
            scale = 10
            quality = 90
            
            # Save temp compressed version
            temp_name = "temp_ela.jpg"
            cv2.imwrite(temp_name, img_cv, [cv2.IMWRITE_JPEG_QUALITY, quality])
            
            # Load and compare
            compressed = cv2.imread(temp_name)
            diff = 15 * cv2.absdiff(img_cv, compressed)
            os.remove(temp_name)
            
            # Apply heatmap color map to the difference
            heatmap = cv2.applyColorMap(diff, cv2.COLORMAP_JET)
            overlay = cv2.addWeighted(img_cv, 0.6, heatmap, 0.4, 0)
        else:
            # If genuine, just return the original with a green border
            overlay = img_cv
            cv2.rectangle(overlay, (0,0), (overlay.shape[1], overlay.shape[0]), (0,255,0), 10)

        # Save result
        filename = os.path.basename(original_path)
        save_path = os.path.join(output_folder, f"heatmap_{filename}")
        os.makedirs(output_folder, exist_ok=True)
        cv2.imwrite(save_path, overlay)
        
        return save_path