import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import os
import re
from rapidfuzz import fuzz
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TESSERACT_PATH = os.getenv('TESSERACT_PATH')
if TESSERACT_PATH:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
    logger.info(f"Using Tesseract from {TESSERACT_PATH}")
else:
    logger.warning("TESSERACT_PATH not set. Using system default.")

def extract_text_from_pdf_or_image(file_path):
    text = ''
    if file_path.lower().endswith('.pdf'):
        images = convert_from_path(file_path)
    else:
        images = [Image.open(file_path)]

    for img in images:
        text += pytesseract.image_to_string(img)
    return text

def extract_po_invoice_info(text, filename, doc_type):
    info = {
        'filename': filename,
        'text': text,
        'po_number': None,
        'invoice_number': None,
        'date': None,
        'amount': None,
        'type': doc_type
    }

    po_match = re.search(r'PO\s*Number[:\s]*([A-Z0-9\-]+)', text, re.IGNORECASE)
    inv_match = re.search(r'Invoice\s*Number[:\s]*([A-Z0-9\-]+)', text, re.IGNORECASE)
    date_match = re.search(r'\b(\d{2}[/-]\d{2}[/-]\d{4})\b', text)
    amt_match = re.search(r'\b(?:USD|INR|Rs\.?)?\s?([0-9\.,]+)\b', text)

    if po_match:
        info['po_number'] = po_match.group(1).strip()
    if inv_match:
        info['invoice_number'] = inv_match.group(1).strip()
    if date_match:
        info['date'] = date_match.group(1).strip()
    if amt_match:
        info['amount'] = amt_match.group(1).strip()

    return info

def extract_po_invoice_info_from_folder(folder_path, doc_type):
    extracted_data = []
    for fname in os.listdir(folder_path):
        path = os.path.join(folder_path, fname)
        try:
            text = extract_text_from_pdf_or_image(path)
            extracted_data.append(extract_po_invoice_info(text, fname, doc_type))
        except Exception as e:
            logger.error(f"Error processing {fname}: {e}")
    return extracted_data

def match_invoices_with_pos(invoices, pos_list, threshold=80):
    matches = []
    for inv in invoices:
        best_match = None
        best_score = 0
        for po in pos_list:
            if inv['po_number'] and po['po_number']:
                score = fuzz.token_sort_ratio(inv['po_number'], po['po_number'])
                if score > best_score and score >= threshold:
                    best_score = score
                    best_match = po

        matches.append({
            'Invoice File': inv['filename'],
            'Invoice Number': inv['invoice_number'],
            'PO Number (from Invoice)': inv['po_number'],
            'Invoice Date': inv['date'],
            'Invoice Amount': inv['amount'],
            'Matched PO File': best_match['filename'] if best_match else 'Not Found',
            'PO Number (from PO)': best_match['po_number'] if best_match else 'N/A',
            'PO Date': best_match['date'] if best_match else 'N/A',
            'PO Amount': best_match['amount'] if best_match else 'N/A',
            'Match Score': best_score if best_match else 0
        })
    return matches
