from fpdf import FPDF
import os
from datetime import datetime

class FraudReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Insurance Claim Fraud Report', 0, 1, 'C')
        self.ln(5)
        self.set_draw_color(50, 50, 50)
        self.line(10, 25, 200, 25)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}} | AI Sentinel System', 0, 0, 'C')

    def chapter_title(self, label):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(230, 240, 255)
        self.cell(0, 8, f'  {label}', 0, 1, 'L', 1)
        self.ln(4)

    def chapter_body(self, body, color=(0,0,0)):
        self.set_font('Arial', '', 11)
        self.set_text_color(*color)
        self.multi_cell(0, 6, body)
        self.set_text_color(0, 0, 0)
        self.ln()

def generate_claim_report(claim_data, output_dir="reports"):
    """
    Generates a PDF report for a specific claim.
    """
    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    pdf = FraudReport()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # 1. Summary
    pdf.chapter_title("1. Claim Summary")
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 8, f"Claim ID: {claim_data.get('claim_id', 'N/A')}", ln=1)
    pdf.cell(0, 8, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=1)
    pdf.cell(0, 8, f"Risk Level: {claim_data.get('risk_label', 'Unknown')}", ln=1)
    pdf.ln(5)
    
    # 2. Verdict
    pdf.chapter_title("2. AI Fraud Analysis")
    score = claim_data.get('fraud_score', 0.0)
    if score > 0.7:
        pdf.chapter_body(f"CRITICAL RISK DETECTED (Score: {score:.2f})", (200, 0, 0))
    else:
        pdf.chapter_body(f"LOW RISK (Score: {score:.2f})", (0, 150, 0))
        
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 8, "Detected Anomalies:", ln=1)
    pdf.set_font('Arial', '', 10)
    
    anomalies = claim_data.get('anomalies', [])
    if not anomalies:
         pdf.cell(0, 6, " - No significant anomalies found.", ln=1)
    else:
        for item in anomalies:
            pdf.cell(0, 6, f" - {item}", ln=1)
    pdf.ln(10)

    # Output
    filename = f"Fraud_Report_{claim_data.get('claim_id', 'doc')}.pdf"
    filepath = os.path.join(output_dir, filename)
    pdf.output(filepath)
    return filepath