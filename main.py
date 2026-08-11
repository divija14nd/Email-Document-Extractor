import argparse
import json
import sys

from gmail_auth import get_gmail_service
from gmail_client import iter_pdf_attachments
from paths import base_dir
from pdf_utils import decrypt_pdf, extract_text, matching_categories, text_contains

CONFIG_PATH = base_dir() / "config.json"


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(
        description="Extract and organize PDFs from Gmail (bank/NSDL statements by month, plus optional keyword search)"
    )
    parser.add_argument(
        "search_word",
        nargs="?",
        help="Optional word to search for; matches are saved into a folder with this name",
    )
    parser.add_argument(
        "--query",
        default="has:attachment filename:pdf",
        help="Gmail search query to narrow down which emails are scanned",
    )
    args = parser.parse_args()

    config = load_config()
    passwords = config.get("passwords", [])
    categories = config.get("categories", {})

    service = get_gmail_service()

    saved = 0
    for filename, pdf_bytes, received_at in iter_pdf_attachments(service, args.query):
        decrypted = decrypt_pdf(pdf_bytes, passwords)
        if decrypted is None:
            print(f"Skipped (no password worked): {filename}")
            continue

        text = extract_text(decrypted)
        month_folder = received_at.strftime("%Y-%m")
        matched_any = False

        for category in matching_categories(text, categories):
            dest_dir = base_dir() / category / month_folder
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / filename
            dest.write_bytes(decrypted)
            print(f"Saved [{category}]: {dest}")
            matched_any = True
            saved += 1

        if args.search_word and text_contains(text, args.search_word):
            dest_dir = base_dir() / args.search_word
            dest_dir.mkdir(exist_ok=True)
            dest = dest_dir / filename
            dest.write_bytes(decrypted)
            print(f"Saved [{args.search_word}]: {dest}")
            matched_any = True
            saved += 1

        if not matched_any:
            print(f"No match: {filename}")

    print(f"Done. {saved} PDF(s) saved.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"\nError: {exc}")
        if getattr(sys, "frozen", False):
            input("\nPress Enter to exit...")
        raise
    else:
        if getattr(sys, "frozen", False):
            input("\nPress Enter to exit...")
