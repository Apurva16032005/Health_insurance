from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np

class MedicalNLP:
    def __init__(self):
        print("🔹 Loading NLP Model (DistilBERT)...")
        self.tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
        self.model = AutoModel.from_pretrained("distilbert-base-uncased")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

    def get_embedding(self, text):
        """
        Converts full bill text into a 768-dimensional vector.
        """
        # Truncate to 512 tokens (BERT limit)
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        # Use the [CLS] token embedding (first token) as the sentence representation
        cls_embedding = outputs.last_hidden_state[:, 0, :].cpu().numpy()
        return cls_embedding.flatten() # Returns shape (768,)

    def extract_medical_entities(self, text):
        """
        Simple keyword extraction for demo. 
        In production, replace with a refined NER model (e.g., en_ner_bc5cdr_md).
        """
        keywords = []
        suspicious_keywords = ["edited", "sample", "template", "test"]
        medical_keywords = ["diagnosis", "patient", "hospital", "treatment", "surgery", "fever", "dengue"]
        
        lower_text = text.lower()
        
        found_medical = [w for w in medical_keywords if w in lower_text]
        found_suspicious = [w for w in suspicious_keywords if w in lower_text]
        
        return {
            "medical_context": found_medical,
            "suspicious_flags": found_suspicious,
            "is_medical_bill": len(found_medical) > 0
        }