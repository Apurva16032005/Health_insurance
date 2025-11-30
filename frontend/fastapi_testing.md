# FASTAPI TESTING GUIDE

## 1. Start Backend
Run:

uvicorn app:app --host 0.0.0.0 --port 8000 --reload

## 2. Test /upload-claim manually

### Using curl:
curl -X POST "http://localhost:8000/upload-claim" \
  -F "bill_image=@sample.jpg" \
  -F "claim_amount=5000" \
  -F "description=fracture treatment"

### Using Postman:
POST → http://localhost:8000/upload-claim
Body → form-data:
    bill_image : <select file>
    claim_amount : 5000
    description : fracture treatment

## 3. Expected JSON Output
- final decision
- ocr text
- extracted fields
- fraud score
- tamper score
- forensic score
- NLP outputs
- XAI paths

## 4. Debugging
- Check uploads/ folder
- Check reports/explainability/
- Check console for model loading errors

