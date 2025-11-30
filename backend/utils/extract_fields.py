import re

def extract_key_fields(raw_text):
    """
    Parses unstructured OCR text to find entities using Regex.
    Target Fields: Invoice No, Date, Total Amount, GST No.
    """
    data = {
        "invoice_no": None,
        "date": None,
        "total_amount": 0.0,
        "gst_no": None,
        "hospital_name": None
    }

    # 1. Extract Date (Formats: DD/MM/YYYY, DD-MM-YYYY, YYYY-MM-DD)
    date_pattern = r'\b(\d{2}[/-]\d{2}[/-]\d{4})\b'
    date_match = re.search(date_pattern, raw_text)
    if date_match:
        data["date"] = date_match.group(1)

    # 2. Extract Total Amount (Look for largest number near keywords)
    # Pattern looks for currency symbols or numbers with 2 decimals
    # We look for lines containing "Total" or "Net" first
    lines = raw_text.split('\n')
    for line in lines:
        if any(x in line.lower() for x in ['total', 'amount', 'net', 'payable']):
            # Find number in this line
            nums = re.findall(r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', line)
            if nums:
                # Convert last found number to float (usually the final total)
                try:
                    clean_num = nums[-1].replace(',', '')
                    data["total_amount"] = float(clean_num)
                except:
                    pass

    # 3. Extract GST (Indian GST is 15 chars alphanumeric)
    gst_pattern = r'\b\d{2}[A-Z]{5}\d{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}\b'
    gst_match = re.search(gst_pattern, raw_text)
    if gst_match:
        data["gst_no"] = gst_match.group(0)

    # 4. Extract Invoice Number
    inv_pattern = r'(?i)(?:invoice|bill)\s*no[:\.]?\s*([a-zA-Z0-9/-]+)'
    inv_match = re.search(inv_pattern, raw_text)
    if inv_match:
        data["invoice_no"] = inv_match.group(1)

    return data