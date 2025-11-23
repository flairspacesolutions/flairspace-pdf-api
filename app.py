from flask import Flask, request, jsonify, send_from_directory, abort
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import mm
import uuid, os, datetime

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "files")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = Flask(__name__, static_folder="files")

def create_pdf(path, title, data: dict):
    doc = SimpleDocTemplate(path, pagesize=A4,
                            rightMargin=20*mm, leftMargin=20*mm,
                            topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph(title, styles['Title']))
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"Generated: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", styles['Normal']))
    story.append(Spacer(1, 12))
    for k, v in data.items():
        story.append(Paragraph(f"<b>{k}:</b> {v}", styles['Normal']))
        story.append(Spacer(1,6))
    doc.build(story)

@app.route('/api/generate', methods=['POST'])
def generate():
    if not request.is_json:
        return jsonify({"error": "Expected JSON body"}), 400
    body = request.get_json()
    template_type = body.get('templateType')
    data = body.get('data') or {}

    if not template_type:
        return jsonify({"error": "templateType is required"}), 400
    if not isinstance(data, dict):
        return jsonify({"error": "data must be an object"}), 400

    title_map = {
        "rent_receipt": "Rent Receipt",
        "tenancy_agreement": "Tenancy Agreement",
        "notice": "Notice Document"
    }

    title = title_map.get(template_type, template_type.replace('_', ' ').title())

    file_id = str(uuid.uuid4())
    filename = f"{file_id}.pdf"
    filepath = os.path.join(UPLOAD_DIR, filename)

    try:
        create_pdf(filepath, title, data)
    except Exception as e:
        return jsonify({"error": "PDF generation failed", "detail": str(e)}), 500

    base = request.host_url.rstrip('/')
    pdf_url = f"{base}/files/{filename}"
    return jsonify({"pdfUrl": pdf_url}), 200

@app.route('/files/<path:filename>', methods=['GET'])
def serve_file(filename):
    safe_dir = os.path.join(os.path.dirname(__file__), "files")
    if os.path.exists(os.path.join(safe_dir, filename)):
        return send_from_directory(safe_dir, filename)
    abort(404)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
