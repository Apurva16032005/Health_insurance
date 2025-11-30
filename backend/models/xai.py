import matplotlib.pyplot as plt
import os

class ExplainabilityModule:
    def __init__(self):
        pass

    def generate_explanation_report(self, claim_id, fraud_results, output_folder="reports/explainability"):
        """
        Generates a summary JSON and potentially a plot explaining the score.
        """
        os.makedirs(output_folder, exist_ok=True)
        
        explanation = {
            "claim_id": claim_id,
            "fraud_score": fraud_results['fraud_score'],
            "primary_reasons": fraud_results['risk_factors'],
            "human_readable_summary": ""
        }
        
        # Generate Text Summary
        if fraud_results['fraud_score'] > 0.7:
            text = f"CRITICAL ALERT: High probability of fraud ({fraud_results['fraud_score']}). "
            text += f"System detected {len(fraud_results['risk_factors'])} anomalies. "
            text += "Primary concern is visual manipulation." if "Visual Tampering" in str(fraud_results['risk_factors']) else ""
        else:
            text = "Document appears genuine. Minor anomalies found but within acceptable range."
            
        explanation['human_readable_summary'] = text
        
        return explanation