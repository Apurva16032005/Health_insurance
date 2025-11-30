import math
from collections import Counter

def check_benford_law(numbers):
    """
    Benford's Law: In real financial data, the leading digit '1' appears ~30% of the time.
    If 'User Typed' numbers are random, they violate this distribution.
    """
    if not numbers or len(numbers) < 5:
        return 0.0 # Not enough data
        
    first_digits = [int(str(n)[0]) for n in numbers if n > 0]
    digit_counts = Counter(first_digits)
    total = len(first_digits)
    
    # Expected frequency for digit 1 is ~30.1%
    actual_1_freq = digit_counts.get(1, 0) / total
    
    # If deviations are extreme, return high suspicion score
    if actual_1_freq < 0.15: # Too few 1s
        return 0.8 # High Fraud Likelihood
    return 0.1 # Low Fraud Likelihood

def apply_business_rules(ocr_data, ml_score, claim_amount):
    """
    Hard rules that override ML models.
    """
    flags = []
    
    # Rule 1: Amount consistency
    extracted_amt = ocr_data.get('structured_data', {}).get('total_amount', 0)
    if extracted_amt > 0:
        if abs(extracted_amt - float(claim_amount)) > 500:
            flags.append("Claim Amount does not match Bill Total")
            
    # Rule 2: Date Check (Simple check if date exists)
    if not ocr_data.get('structured_data', {}).get('date'):
        flags.append("No Date Found on Bill")
        
    # Rule 3: High Value Claim without supporting Diagnosis
    # (This requires the NLP diagnosis output passed in, simplified here)
    if float(claim_amount) > 100000 and ml_score > 0.6:
        flags.append("High Value Claim flagged by AI")

    return flags