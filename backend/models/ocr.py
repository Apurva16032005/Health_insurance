import easyocr
import cv2
import numpy as np
import re

class OCRProcessor:
    def __init__(self):
        print("🔹 Loading EasyOCR Model...")
        # 'en' for English. Add other codes if dealing with local languages.
        self.reader = easyocr.Reader(['en'], gpu=True)

    def extract_text(self, image_path):
        """
        Extracts raw text and bounding boxes.
        Returns: { 'raw_text': str, 'lines': list, 'structured': dict }
        """
        results = self.reader.readtext(image_path)
        
        full_text = " ".join([res[1] for res in results])
        lines = [res[1] for res in results]
        
        # Basic regex extraction for critical fields
        extracted_data = self._parse_critical_fields(lines)
        
        return {
            "raw_text": full_text,
            "lines": lines,
            "structured_data": extracted_data
        }

    def _parse_critical_fields(self, lines):
        """
        Heuristic parsing to find Amounts, Dates, and Bill Numbers.
        """
        data = {"total_amount": None, "date": None, "invoice_no": None}
        
        # Regex Patterns
        date_pattern = r'\d{2}[/-]\d{2}[/-]\d{2,4}'
        # Look for numbers that might be prices (e.g., 50,000.00)
        amount_pattern = r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'

        for line in lines:
            # Find Date
            if not data['date']:
                date_match = re.search(date_pattern, line)
                if date_match:
                    data['date'] = date_match.group(0)

            # Find Amount (naive logic: usually near 'Total' or 'Net')
            if 'Total' in line or 'Amount' in line or 'Net' in line:
                amt_match = re.search(amount_pattern, line)
                if amt_match:
                    try:
                        # Clean string to float
                        amt_str = amt_match.group(0).replace(',', '')
                        data['total_amount'] = float(amt_str)
                    except:
                        pass
        
        return data