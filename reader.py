# Reader Script
import fitz

def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n\n"
    return text.strip()

pdf_path = r"C:\Users\hp\OneDrive\Desktop\nikola.pdf"
pdf_text = extract_text_from_pdf(pdf_path)
print(pdf_text[:500])