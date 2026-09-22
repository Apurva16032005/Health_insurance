import uvicorn
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import mysql.connector
import json
from datetime import datetime

# --- IMPORT YOUR AI MODULES ---
from models.ocr import OCRProcessor
from models.cnn_model import ForgeryDetectionModel
from models.nlp_model import MedicalNLP
from models.ml_model import FraudMLModel
from models.multimodal import MultimodalFusion
from models.xai import ExplainabilityModule

from utils.preprocess import preprocess_for_ocr
from utils.forensics import check_metadata, error_level_analysis
from utils.dedup import check_duplicate
from utils.extract_fields import extract_key_fields
from utils.combine_features import prepare_feature_vector
from utils.validation_rules import check_benford_law
# IMPORT THE NEW REPORT GENERATOR
from utils.report_gen import generate_claim_report
import re

# --- CONFIGURATION ---
app = FastAPI(title="Insurance Fraud Detection System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories
UPLOAD_DIR = "uploads"
REPORT_DIR = "reports"
for d in [UPLOAD_DIR, REPORT_DIR]:
    os.makedirs(d, exist_ok=True)

app.mount("/reports", StaticFiles(directory=REPORT_DIR), name="reports")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# --- DATABASE CONNECTION ---
DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "Apurva@2200",  # Update if you have a password
    "database": "insurance"
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

# --- LOAD AI MODELS ---
print("⏳ Loading AI Models... (This may take a moment)")
ocr_engine = OCRProcessor()
cnn_engine = ForgeryDetectionModel()
nlp_engine = MedicalNLP()
ml_brain = FraudMLModel()
fusion_engine = MultimodalFusion()
xai_engine = ExplainabilityModule()
print("✅ All AI Models Loaded & Ready!")

# --- API ENDPOINTS ---

@app.post("/upload-claim")
async def upload_claim(
    file: UploadFile = File(...),
    amount: float = Form(...),
    user_id: int = Form(...),
    description: str = Form(""),
    hospital_name: str = Form(""),
    patient_name: str = Form("")
):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 1. Save Uploaded File
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        print(f"🚀 Analyzing Claim: {filename} for User {user_id}")

        # 2. Create Database Record
        sql_insert = """
            INSERT INTO claims (user_id, uploaded_filename, claim_amount, description, ai_status, created_at) 
            VALUES (%s, %s, %s, %s, 'processing', NOW())
        """
        cursor.execute(sql_insert, (user_id, filename, amount, description))
        conn.commit()
        claim_id = cursor.lastrowid

        # --- START AI PIPELINE ---
        
        # A. Forensic Analysis
        meta_result = check_metadata(file_path)
        ela_score = error_level_analysis(file_path)
        if ela_score > 0.4:
            meta_result['is_suspicious'] = True
        dedup_result = check_duplicate(file_path, str(claim_id))
        
        # B. Visual Forgery Detection
        cnn_result = cnn_engine.detect_forgery(file_path, output_folder=REPORT_DIR)
        
        # C. Text Analysis
        clean_img = preprocess_for_ocr(file_path)
        ocr_result = ocr_engine.extract_text(clean_img)
        ocr_result['structured_data'] = extract_key_fields(ocr_result['raw_text'])
        
        nlp_embedding = nlp_engine.get_embedding(ocr_result['raw_text'])
        nlp_result = nlp_engine.extract_medical_entities(ocr_result['raw_text'])

        # Benford's Law numeric check
        all_numbers = []
        for word in re.findall(r'\b\d+\b', ocr_result['raw_text']):
            try:
                val = int(word)
                if val > 0:
                    all_numbers.append(val)
            except:
                pass
        benford_score = check_benford_law(all_numbers)

        # D. ML Fraud Prediction
        features = prepare_feature_vector(ocr_result, cnn_result, nlp_result, meta_result, amount)
        ml_prob = ml_brain.predict(features)
        
        # E. Multimodal Fusion
        visual_score = max(cnn_result['score'], ela_score)
        fusion_result = fusion_engine.predict_fraud_score(
            nlp_embedding, visual_score, ocr_result, amount
        )
        
        # Add ELA risk factor if high
        if ela_score > 0.4:
            fusion_result['risk_factors'].append(f"ELA Forgery Pattern Detected (Score: {ela_score:.2f})")
            
        # Add Benford's Law risk factor if high
        if benford_score > 0.5:
            fusion_result['risk_factors'].append("Benford's Law Anomaly: Suspicious number distribution")
            
        # Add Layout Match risk factor if mismatch
        if hospital_name:
            from utils.layout_match import match_template
            layout_result = match_template(file_path, hospital_name)
            if layout_result.get('match_score', 1.0) < 0.4 and layout_result.get('status') == "Layout Mismatch":
                fusion_result['risk_factors'].append(f"Layout Mismatch: Bill deviates from {hospital_name} template")

        final_score = (fusion_result['fraud_score'] * 0.6) + (ml_prob * 0.4)
        
        if dedup_result['is_duplicate']:
            final_score = 1.0
            fusion_result['risk_factors'].append("Duplicate Bill Detected")

        risk_label = "High" if final_score > 0.7 else "Medium" if final_score > 0.3 else "Low"

        # F. Generate Explanation
        xai_report = xai_engine.generate_explanation_report(
            claim_id, 
            {"fraud_score": final_score, "risk_factors": fusion_result['risk_factors']}
        )

        # G. Generate PDF Report (NEW ADDITION)
        # This calls the new utility script to create the PDF
        report_path = generate_claim_report({
            "claim_id": str(claim_id),
            "fraud_score": final_score,
            "risk_label": risk_label,
            "anomalies": fusion_result['risk_factors']
        }, output_dir=REPORT_DIR)
        print(f"📄 Report generated: {report_path}")

        # 3. Save Results to Database
        sql_update = "UPDATE claims SET ai_status = 'completed' WHERE id = %s"
        cursor.execute(sql_update, (claim_id,))
        
        # Extract structured fields
        extracted_amt = ocr_result.get('structured_data', {}).get('total_amount', 0.0)
        bill_date = ocr_result.get('structured_data', {}).get('date', None)
        ocr_hosp = ocr_result.get('structured_data', {}).get('hospital_name', None) or hospital_name
        gst_no = ocr_result.get('structured_data', {}).get('gst_no', None)

        sql_ai_data = """
            INSERT INTO claim_ai_data (
                claim_id, fraud_score, tamper_score, ocr_text, risk_label, 
                extracted_amount, bill_date, hospital_name, gst_number, created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """
        cursor.execute(sql_ai_data, (
            claim_id, final_score, visual_score, ocr_result['raw_text'][:1000], risk_label,
            extracted_amt, bill_date, ocr_hosp, gst_no
        ))
        
        sql_xai = "INSERT INTO claim_xai (claim_id, explanation_text) VALUES (%s, %s)"
        cursor.execute(sql_xai, (claim_id, xai_report['human_readable_summary']))
        
        conn.commit()
        
        return {
            "status": "success",
            "claim_id": claim_id,
            "fraud_score": round(final_score, 2),
            "risk_label": risk_label,
            "message": "Claim processed successfully."
        }

    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.get("/get-pending-claims")
def get_claims():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # We join the tables directly instead of relying on the old View
    # This ensures we get the latest data structure
    query = """
        SELECT 
            c.id AS claim_id, 
            c.created_at, 
            c.claim_amount, 
            c.uploaded_filename, 
            c.description, 
            c.ai_status,
            a.fraud_score, 
            a.tamper_score, 
            a.risk_label,
            a.hospital_name,
            a.extracted_amount,
            a.bill_date,
            a.gst_number,
            x.explanation_text
        FROM claims c
        LEFT JOIN claim_ai_data a ON c.id = a.claim_id
        LEFT JOIN claim_xai x ON c.id = x.claim_id
        WHERE c.ai_status = 'completed'
        ORDER BY c.created_at DESC
    """
    
    cursor.execute(query)
    claims = cursor.fetchall()
    
    # Reformat flat DB rows into the Nested JSON the frontend expects
    formatted_claims = []
    for r in claims:
        # Handle missing values if AI hasn't run perfectly
        f_score = r['fraud_score'] if r['fraud_score'] is not None else 0.0
        t_score = r['tamper_score'] if r['tamper_score'] is not None else 0.0
        hosp = r['hospital_name'] if r['hospital_name'] else "Unknown"
        
        formatted_claims.append({
            "claim_id": r['claim_id'],
            "created_at": str(r['created_at']),
            "status": r['ai_status'],
            "input_data": {
                "amount_claimed": r['claim_amount'],
                "hospital_name": hosp,
                "file_url": f"/uploads/{r['uploaded_filename']}"
            },
            "scores": {
                "final_fraud_score": f_score,
                "cnn_score": t_score
            },
            "details": {
                "risk_label": r['risk_label'],
                "extracted_amount": str(r['extracted_amount']) if r['extracted_amount'] is not None else "0.00",
                "bill_date": r['bill_date'],
                "gst_number": r['gst_number'],
                "cnn_heatmap": f"/reports/heatmap_{r['uploaded_filename']}" if t_score > 0.4 else "/reports/temp_heatmap.png"
            },
            "xai_explanation": r['explanation_text'] or "Analysis complete. Review attached report."
        })
        
    cursor.close()
    conn.close()
    return formatted_claims

@app.post("/update-decision")
def update_decision(data: dict):
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = "UPDATE claims SET officer_decision = %s, officer_comments = %s, ai_status = 'reviewed' WHERE id = %s"
    cursor.execute(sql, (data['status'], data['remarks'], data['claim_id']))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Decision updated"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)