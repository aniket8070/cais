import io
import re
import pytesseract
from pdf2image import convert_from_bytes

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
POPPLER_PATH = r'C:\Release-25.12.0-0\poppler-25.12.0\Library\bin'

# Process only first 15 pages — enough for UPSC notes
MAX_PAGES = 15


def extract_text(file):
    """PDF → OCR → Text (batch processing to avoid memory issues)"""
    try:
        if hasattr(file, 'read'):
            pdf_bytes = file.read()
        else:
            with open(file, 'rb') as f:
                pdf_bytes = f.read()

        print(f"[OCR] Starting extraction (max {MAX_PAGES} pages)...")
        text = ""

        # Process pages in small batches to avoid RAM issues
        for batch_start in range(1, MAX_PAGES + 1, 3):
            batch_end = min(batch_start + 2, MAX_PAGES)
            try:
                images = convert_from_bytes(
                    pdf_bytes,
                    dpi=150,              # Lower DPI = less RAM
                    poppler_path=POPPLER_PATH,
                    fmt='jpeg',
                    first_page=batch_start,
                    last_page=batch_end,
                    thread_count=1
                )
                for i, img in enumerate(images):
                    page_num = batch_start + i
                    # Resize image to save memory
                    w, h = img.size
                    if w > 1200:
                        ratio = 1200 / w
                        img = img.resize((1200, int(h * ratio)))

                    page_text = pytesseract.image_to_string(
                        img,
                        lang='eng',
                        config='--psm 6 --oem 1'
                    )
                    if page_text.strip():
                        text += page_text + "\n"
                        print(f"[OCR] Page {page_num}: {len(page_text)} chars ✓")
                    else:
                        print(f"[OCR] Page {page_num}: 0 chars")

                    # Free memory
                    del img
                del images

            except Exception as e:
                print(f"[OCR] Batch {batch_start}-{batch_end} error: {e}")
                continue

        cleaned = _clean_text(text)
        print(f"[OCR] Final: {len(cleaned)} chars")
        print(f"[OCR] Sample: {cleaned[:300]}")
        return cleaned

    except Exception as e:
        print(f"[OCR] Fatal error: {e}")
        return ""


def _clean_text(text):
    if not text:
        return ""
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    text = text.replace('\u2018', "'").replace('\u2019', "'")
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    text = text.replace('\u2013', '-').replace('\u2014', '-')
    text = text.replace('\u00a0', ' ')
    text = re.sub(r'[ \t]{4,}', ' ', text)
    lines = text.split('\n')
    clean = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        words = re.findall(r'[a-zA-Z]{3,}', line)
        if len(words) >= 2:
            clean.append(line)
    result = '\n'.join(clean)
    result = re.sub(r'\n{4,}', '\n\n', result)
    return result.strip()