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


def matching_categories(text, sender, categories):
    text_lower = text.lower()
    sender_lower = (sender or "").lower()
    matches = []
    for category, rule in categories.items():
        keywords = rule.get("keywords", [])
        senders = rule.get("senders", [])
        keyword_hit = any(keyword.lower() in text_lower for keyword in keywords)
        sender_hit = any(pattern.lower() in sender_lower for pattern in senders)
        if keyword_hit or sender_hit:
            matches.append(category)
    return matches
