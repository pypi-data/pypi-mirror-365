import os
import mimetypes
from pralekh.pdf_handler import handle_pdf
from pralekh.docx_handler import handle_docx
from pralekh.pptx_handler import handle_pptx
from pralekh.xlsx_handler import handle_xlsx
from pralekh.txt_handler import handle_txt

def extract(file_path, output_format="text"):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return handle_pdf(file_path, output_format)
    elif ext == ".docx":
        return handle_docx(file_path, output_format)
    elif ext == ".pptx":
        return handle_pptx(file_path, output_format)
    elif ext == ".xlsx":
        return handle_xlsx(file_path, output_format)
    elif ext == ".txt":
        return handle_txt(file_path, output_format)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
