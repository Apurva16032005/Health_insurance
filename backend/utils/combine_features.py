import numpy as np

def prepare_feature_vector(ocr_data, cnn_results, nlp_results, metadata_results, claimed_amount):
    """
    Aggregates all signals into a single feature vector for the ML Classifier.
    
    Output Vector Structure (Example):
    [
      cnn_tamper_score,      # (0-1)
      metadata_suspicious,   # (0 or 1)
      amount_mismatch_ratio, # (Claimed / Extracted)
      text_keyword_density,  # (Medical keywords found count)
      nlp_risk_score         # (Derived from embeddings)
    ]
    """
    
    # 1. CNN Score (Visual Tampering)
    f1 = cnn_results.get('score', 0.0)
    
    # 2. Metadata Check
    f2 = 1.0 if metadata_results.get('is_suspicious') else 0.0
    
    # 3. Amount Mismatch (Behavioral Fraud)
    extracted_amt = ocr_data.get('structured_data', {}).get('total_amount', 0.0)
    if extracted_amt > 0:
        # Calculate ratio deviation (e.g., 1.0 = match, 2.0 = user claimed double)
        f3 = float(claimed_amount) / extracted_amt
        # Normalize: we care about deviation from 1.0
        f3 = abs(f3 - 1.0)
    else:
        f3 = 0.5 # Penalty for not finding amount
        
    # 4. Medical Context (NLP)
    # Assuming nlp_results gives a "medical_confidence" or simply count of entities
    med_keywords = nlp_results.get('medical_context', [])
    f4 = len(med_keywords) # Higher is usually better (more medical context)
    
    # Create Vector
    # Note: This shape must match what your ml_model.py was trained on!
    features = [f1, f2, f3, f4]
    
    return np.array(features)