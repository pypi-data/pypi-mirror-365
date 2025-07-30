def run_app():
    from flask import Flask, render_template, request, send_file, redirect, url_for, session
    import os
    import pandas as pd
    from tcai_pay_x.utils.ocr_utils import extract_po_invoice_info_from_folder, match_invoices_with_pos

    app = Flask(__name__)
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dummy_key")

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    INVOICE_FOLDER = os.path.join(UPLOAD_FOLDER, 'invoices')
    PO_FOLDER = os.path.join(UPLOAD_FOLDER, 'pos')
    OUTPUT_FILE = os.path.join(UPLOAD_FOLDER, 'matched_output.xlsx')

    os.makedirs(INVOICE_FOLDER, exist_ok=True)
    os.makedirs(PO_FOLDER, exist_ok=True)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/upload', methods=['POST'])
    def upload():
        threshold = int(request.form.get('threshold', 80))

        # Clean previous uploads
        for folder in [INVOICE_FOLDER, PO_FOLDER]:
            for f in os.listdir(folder):
                os.remove(os.path.join(folder, f))

        # Save new files
        for f in request.files.getlist('invoices'):
            f.save(os.path.join(INVOICE_FOLDER, f.filename))

        for f in request.files.getlist('pos'):
            f.save(os.path.join(PO_FOLDER, f.filename))

        # Perform OCR and matching
        invoices_info = extract_po_invoice_info_from_folder(INVOICE_FOLDER, doc_type='invoice')
        pos_info = extract_po_invoice_info_from_folder(PO_FOLDER, doc_type='po')
        matches = match_invoices_with_pos(invoices_info, pos_info, threshold=threshold)

        df = pd.DataFrame(matches)
        df.to_excel(OUTPUT_FILE, index=False)  # Save to a known path

        session['matches'] = matches
        return redirect(url_for('preview'))

    @app.route('/preview')
    def preview():
        matches = session.get('matches', [])
        return render_template('preview.html', matches=matches)

    @app.route('/download')
    def download():
        return send_file(OUTPUT_FILE, as_attachment=True)

    app.run(debug=True)

if __name__ == "__main__":
    run_app()
