import os
try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

def read_pdf_content(file_path: str) -> dict:
    if PdfReader is None:
        return {"error": "pypdf library is not installed."}
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return {"filename": os.path.basename(file_path), "content": text}
    except Exception as e:
        return {"error": f"Failed to read PDF: {str(e)}"}