# Health Insurance Claim Checker (FraudShield AI)

An intelligent multimodal AI system designed to detect incorrect, fraudulent, or mismatched health insurance claims. The application analyzes submitted claim documents (bills, receipts, etc.) and customer details to evaluate their authenticity using a combination of image forensics, OCR, NLP, and Explainable AI.

## Features
- **Claim Verification:** Compares customer details with claim details and flags suspicious or mismatched fields.
- **OCR & NLP Extraction:** Extracts text from medical bills and discharge summaries (using tools like EasyOCR) and interprets medical terms using NLP.
- **Image Forensics & ML:** Detects document forgery and tampering using Convolutional Neural Networks (CNN) and classifies claims (Legitimate, Suspicious, Fraud).
- **Explainable AI (XAI):** Provides transparent reasoning (e.g., using SHAP/LIME) for why a claim might be flagged as fraudulent.

## Project Structure
- `backend/`: The FastAPI backend containing the core AI models, forensics utilities, and API endpoints.
- `frontend/`: The Streamlit web dashboard for uploading claims, visualizing analytics, and viewing fraud analysis results.
- `data/`: Contains sample bills, generated model outputs, and test data.

## Setup Instructions

### 1. Prerequisites
Ensure you have Python 3.10+ installed. It is recommended to use a virtual environment.

```bash
# Create and activate a virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
```

### 2. Install Dependencies
Install the required packages for both the backend and frontend.

### 3. Running the Backend
The backend runs on FastAPI.

```bash
cd backend
uvicorn app:app --reload
```
The API will be available at `http://localhost:8000`.

### 4. Running the Frontend
The frontend dashboard uses Streamlit.

```bash
cd frontend
streamlit run streamlit_app.py
```
The dashboard will open in your browser at `http://localhost:8501`.
