# 📄 Invoice-PO Mapper

A Flask-based web application to match **invoices** with **purchase orders** using **OCR** and **fuzzy matching**. Upload folders of scanned PDFs or images, extract text using OCR, match records with fuzzy logic, preview them in the browser, and export the result to Excel.

---

## 🚀 Features

- 📄 **OCR Extraction** from scanned invoices and POs (PDFs or images)
- 🔍 **Fuzzy Matching** between extracted PO numbers
- 📊 **Excel Export** of matched results
- 🌐 **Flask Web Interface** for file uploads, match preview, and download

---

## 💻 Requirements (Windows Only)

This app requires **Tesseract OCR** and **Poppler for Windows** to function properly.

### ✅ Step 1: Install Tesseract

- Download from the official Windows installer (UB Mannheim build):  
  👉 https://github.com/UB-Mannheim/tesseract/wiki

- After installation, add the Tesseract path to your system environment variables:  
  Example path: `C:\Program Files\Tesseract-OCR`

### ✅ Step 2: Install Poppler

- Download Poppler for Windows:  
  👉 https://github.com/oschwartz10612/poppler-windows/releases/

- Unzip to a folder (e.g., `C:\poppler`)

- Add the binary path to your system environment variables:  
  Example path: `C:\poppler\Library\bin`