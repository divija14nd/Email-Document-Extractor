# Email PDF Extractor

Scans a Gmail inbox for PDF attachments and unlocks password-protected ones
using a known set of passwords. Every unlocked PDF is checked against:

- **Built-in categories** (bank statements, NSDL statements) — matches are
  filed into `<Category>/<YYYY-MM>/`, using the month the email was received.
- **An optional custom search word** you pass on the command line — matches
  are filed into a folder named after that word.

A single PDF can match more than one of these and gets saved into each
matching folder.

The recipient does **not** need Python installed — they get a standalone
`EmailExtractor.exe` built by CI. Only the person setting this up (you) needs
Python, to run it locally during development.

## One-time setup (do this once, before handing the tool off)

1. **Create OAuth credentials** (needed because the tool reads Gmail on the
   recipient's behalf):
   - Go to the [Google Cloud Console](https://console.cloud.google.com/), create a project.
   - Enable the **Gmail API** for that project.
   - Configure the **OAuth consent screen** (External, Testing is fine). Add
     the recipient's Gmail address as a test user.
   - Create an **OAuth client ID** of type **Desktop app**.
   - Download the resulting file and save it as `credentials.json`.
2. **Set the known passwords and category keywords** in `config.json`:
   ```json
   {
     "passwords": ["password1", "password2", "password3", "password4"],
     "categories": {
       "Bank Statements": ["account statement", "statement of account", "bank statement"],
       "NSDL Statements": ["nsdl", "depository", "demat account statement", "consolidated account statement"]
     }
   }
   ```
   A PDF is filed under a category if any of its keywords appear in the PDF's
   text. Add/remove keywords or whole categories as needed — the folder name
   is taken directly from the category key.

## Building the Windows executable

Every push to `main` triggers a GitHub Actions workflow
(`.github/workflows/build-windows.yml`) that builds `EmailExtractor.exe` on a
real Windows runner, smoke-tests it (`EmailExtractor.exe --help`), and
uploads it as a build artifact named `EmailExtractor-windows`. You can also
trigger it manually from the Actions tab ("Run workflow").

Download that artifact from the Actions run — it contains `EmailExtractor.exe`,
`config.json`, and `README.md`. `credentials.json` is intentionally **not**
included (it's a secret and isn't committed to the repo), so add your
`credentials.json` into that downloaded folder before zipping it up for the
recipient.

## Handing off to the recipient

Zip up: `EmailExtractor.exe`, `config.json` (with real passwords/keywords
filled in), and `credentials.json`. Send that zip to the recipient — nothing
else to install.

## Running it (recipient side)

Double-click `EmailExtractor.exe`. This fetches and organizes bank/NSDL
statements by month (no keyword needed) and keeps the console window open
until they press Enter, so any errors are readable.

To also search for a custom word, they run it from Command Prompt instead of
double-clicking:

```
EmailExtractor.exe "invoice"
```

The first run opens a browser window asking the recipient to sign in to
Google and approve read-only Gmail access. After approving once, a
`token.json` is cached next to the exe so future runs don't ask again.

Output layout (created next to the exe):

```
Bank Statements/2026-03/statement.pdf
NSDL Statements/2026-03/cas.pdf
invoice/some_invoice.pdf   (only if a search word was given)
```

Optional: narrow which emails are scanned with `--query`, using normal Gmail
search syntax:

```
EmailExtractor.exe --query "from:billing@example.com has:attachment filename:pdf"
EmailExtractor.exe "invoice" --query "from:billing@example.com has:attachment filename:pdf"
```

## Running it locally during development (macOS/Linux/Windows with Python)

```
pip install -r requirements.txt
python main.py
```
