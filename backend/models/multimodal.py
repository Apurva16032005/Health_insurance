import numpy as np

class MultimodalFusion:
    def __init__(self):
        pass

    def predict_fraud_score(self, nlp_embedding, cnn_score, ocr_data, claimed_amount):
        """
        Combines various AI signals into a single Fraud Score.
        """
        # 1. Heuristic Rules (Base Score)
        base_score = 0.0
        risk_factors = []

        # 2. Visual Tampering (CNN) - High weight
        if cnn_score > 0.7:
            base_score += 0.4
            risk_factors.append(f"High Image Manipulation Detected ({cnn_score:.2f})")
        
        # 3. Amount Anomaly (OCR vs Claimed)
        extracted_amount = ocr_data.get('structured_data', {}).get('total_amount', 0)
        if extracted_amount > 0:
            # If claimed amount is > 20% more than bill amount
            if claimed_amount > (extracted_amount * 1.2):
                base_score += 0.3
                risk_factors.append(f"Amount Mismatch: Bill says {extracted_amount}, User claims {claimed_amount}")
        
        # 4. Text Consistency (NLP)
        # (Simplified: If embedding vector magnitude is unusual, flag it)
        # In production, this compares against valid medical bill clusters
        
        # Fusion Calculation
        # We fuse the base logic with the pure CNN score
        final_score = max(base_score, cnn_score)
        
        # Cap at 0.99
        final_score = min(final_score, 0.99)

        return {
            "fraud_score": round(final_score, 2),
            "risk_factors": risk_factors
        }