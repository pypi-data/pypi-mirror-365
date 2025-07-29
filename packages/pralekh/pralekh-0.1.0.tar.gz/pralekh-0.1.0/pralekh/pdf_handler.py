import pdfplumber
import pytesseract
from PIL import Image
import io
from multiprocessing import Pool, cpu_count

def ocr_page_image(image_bytes):
    image = Image.open(io.BytesIO(image_bytes))
    return pytesseract.image_to_string(image)

def handle_pdf(path, output_format="text"):
    result = {"text": "", "tables": []}
    ocr_images = []
    ocr_indices = []
    texts = []

    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if not text or len(text.strip()) < 10:
                img = page.to_image(resolution=300).original
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                ocr_images.append(buf.getvalue())
                ocr_indices.append(i)
                texts.append(None)
            else:
                texts.append(text)

            tables = page.extract_tables()
            for tbl in tables:
                result["tables"].append(tbl)

    if ocr_images:
        with Pool(min(cpu_count(), len(ocr_images))) as pool:
            ocr_results = pool.map(ocr_page_image, ocr_images)
        for idx, ocr_text in zip(ocr_indices, ocr_results):
            texts[idx] = ocr_text

    result["text"] = "\n".join(texts)
    return result["text"] if output_format == "text" else result
