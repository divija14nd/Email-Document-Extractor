import io

import pdfplumber
import pikepdf


def decrypt_pdf(pdf_bytes, passwords):
    try:
        with pikepdf.open(io.BytesIO(pdf_bytes)) as pdf:
            return _pdf_to_bytes(pdf)
    except pikepdf.PasswordError:
        pass
    except Exception:
        return None

    for password in passwords:
        try:
            with pikepdf.open(io.BytesIO(pdf_bytes), password=password) as pdf:
                return _pdf_to_bytes(pdf)
        except pikepdf.PasswordError:
            continue
        except Exception:
            continue

    return None


def _pdf_to_bytes(pdf):
    buffer = io.BytesIO()
    pdf.save(buffer)
    return buffer.getvalue()


def extract_text(pdf_bytes):
    text_parts = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            text_parts.append(page.extract_text() or "")
    return "\n".join(text_parts)


def text_contains(text, word):
    return word.lower() in text.lower()


def matching_categories(text, categories):
    text_lower = text.lower()
    return [
        category
        for category, keywords in categories.items()
        if any(keyword.lower() in text_lower for keyword in keywords)
    ]
