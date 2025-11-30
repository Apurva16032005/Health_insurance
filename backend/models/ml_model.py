import numpy as np
import pickle
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# Path to the model file (ensure this matches where your notebook saved it!)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "ml_model.pkl")

class FraudMLModel:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.load_model()

    def load_model(self):
        """
        Loads the trained model from disk.
        If missing, it creates a dummy model so the server doesn't crash.
        """
        if os.path.exists(MODEL_PATH):
            print(f"🔹 Loading ML Model from: {MODEL_PATH}")
            try:
                with open(MODEL_PATH, "rb") as f:
                    data = pickle.load(f)
                    self.model = data['model']
                    self.scaler = data['scaler']
                print("✅ ML Model Loaded Successfully")
            except Exception as e:
                print(f"⚠️ Error loading model: {e}")
                self._train_dummy_model()
        else:
            print("⚠️ Model file not found. Training temporary dummy model...")
            self._train_dummy_model()

    def _train_dummy_model(self):
        """Trains a simple fallback model if the real one isn't found."""
        X_dummy = np.random.rand(10, 4)
        y_dummy = np.random.randint(0, 2, 10)
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X_dummy)
        self.model = RandomForestClassifier()
        self.model.fit(X_scaled, y_dummy)
        print("⚠️ Dummy model active (Run notebook to train real model)")

    def predict(self, features):
        """
        Predicts fraud probability.
        Input features: [CNN_Score, Meta_Flag, Amount_Anomaly, NLP_Score]
        """
        if not self.model or not self.scaler:
            return 0.5
            
        try:
            # Reshape and scale
            features_array = np.array(features).reshape(1, -1)
            features_scaled = self.scaler.transform(features_array)
            
            # Get probability of Fraud (Class 1)
            fraud_prob = self.model.predict_proba(features_scaled)[0][1]
            return round(fraud_prob, 4)
        except Exception as e:
            print(f"Prediction Error: {e}")
            return 0.5