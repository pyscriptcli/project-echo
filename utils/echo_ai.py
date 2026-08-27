import os
import re
import sys
import json
import urllib.parse
from pathlib import Path
import requests
import pandas as pd
from pypdf import PdfReader
from docx import Document
from pptx import Presentation
from supabase import create_client, Client

# --- Configuration ---
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "").strip()
DEEPSEEK_CHAT_URL = "https://api.deepseek.com/chat/completions"

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "").strip()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None


# ==========================================
# 1. Multi-Format Text Extraction Layer
# ==========================================

def extract_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    text_chunks = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(text_chunks)


def extract_from_docx(file_path: str) -> str:
    doc = Document(file_path)
    lines = []
    for p in doc.paragraphs:
        if p.text.strip():
            lines.append(p.text.strip())
    for table in doc.tables:
        for row in table.rows:
            row_vals = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if row_vals:
                lines.append(" | ".join(row_vals))
    return "\n".join(lines)


def extract_from_pptx(file_path: str) -> str:
    prs = Presentation(file_path)
    text_lines = []
    for slide_idx, slide in enumerate(prs.slides):
        text_lines.append(f"\n--- Slide {slide_idx + 1} ---")
        for shape in slide.shapes:
            if shape.has_text_frame:
                for paragraph in shape.text_frame.paragraphs:
                    if paragraph.text.strip():
                        text_lines.append(paragraph.text.strip())
            elif shape.has_table:
                for row in shape.table.rows:
                    row_vals = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                    if row_vals:
                        text_lines.append(" | ".join(row_vals))
    return "\n".join(text_lines)


def extract_from_spreadsheet(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    lines = []
    if ext == ".csv":
        df = pd.read_csv(file_path)
        lines.append(df.to_string(index=False))
    else:
        excel_file = pd.ExcelFile(file_path)
        for sheet_name in excel_file.sheet_names:
            lines.append(f"\n--- Sheet: {sheet_name} ---")
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            df = df.dropna(how="all").dropna(axis=1, how="all")
            lines.append(df.to_string(index=False))
    return "\n".join(lines)


def extract_from_plaintext(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def load_document_text(file_path: str) -> str:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_from_pdf(file_path)
    elif ext in [".docx", ".doc"]:
        return extract_from_docx(file_path)
    elif ext in [".pptx", ".ppt"]:
        return extract_from_pptx(file_path)
    elif ext in [".xlsx", ".xls", ".csv"]:
        return extract_from_spreadsheet(file_path)
    elif ext in [".txt", ".md", ".json"]:
        return extract_from_plaintext(file_path)
    else:
        raise ValueError(f"Unsupported format '{ext}'. Supported: .pdf, .docx, .pptx, .xlsx, .csv, .txt, .md")


# ==========================================
# 2. Text Chunking & LLM Structuring Layer
# ==========================================

def chunk_text(text: str, chunk_size: int = 12000, overlap: int = 1000) -> list[str]:
    chunks = []
    start = 0
    clean_text = text.strip()
    if not clean_text:
        return []
    while start < len(clean_text):
        end = start + chunk_size
        chunks.append(clean_text[start:end])
        start += chunk_size - overlap
    return chunks


def extract_entities_with_llm(text_chunk: str) -> list[dict]:
    if not DEEPSEEK_API_KEY:
        print("  [Notice] DEEPSEEK_API_KEY missing. Skipping LLM structuring.")
        return []

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    system_prompt = (
        "You are an enterprise knowledge extraction AI for PRIME Philippines. "
        "Extract all actionable knowledge into a JSON object with key 'items'. "
        "Schema for each item:\n"
        "- category: Exactly one of ['team', 'projects', 'jargon']\n"
        "- key: Canonical name, abbreviation, or entity title (e.g. 'CAPEX', 'Project Echo', 'John Doe')\n"
        "- value: Exhaustive description, definition, role, or scope\n"
        "- priority: Integer from 1 (contextual) to 5 (mission critical)"
    )

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Extract entities from this content:\n\n{text_chunk}"}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.1,
        "max_tokens": 1500
    }

    try:
        resp = requests.post(DEEPSEEK_CHAT_URL, headers=headers, json=payload, timeout=60)
        if resp.status_code == 200:
            parsed = json.loads(resp.json()["choices"][0]["message"]["content"])
            return parsed.get("items", [])
        print(f"  [API Error] Status {resp.status_code}: {resp.text}")
        return []
    except Exception as e:
        print(f"  [Error] LLM request failed: {e}")
        return []


def upsert_to_supabase(items: list[dict]):
    if not supabase:
        print("  [Database] Supabase not connected. Skipping DB upsert.")
        return

    success = 0
    for item in items:
        try:
            payload = {
                "category": str(item.get("category", "jargon")).lower().strip(),
                "key": str(item.get("key", "")).strip(),
                "value": str(item.get("value", "")).strip(),
                "priority": int(item.get("priority", 1))
            }
            if payload["key"] and payload["value"]:
                supabase.table("echo_context").upsert(payload, on_conflict="category,key").execute()
                success += 1
        except Exception as e:
            print(f"  [DB Error] Failed to write '{item.get('key')}': {e}")
    print(f"  [Database] Successfully synced {success}/{len(items)} items to Supabase.")


# ==========================================
# 3. Helpers: Path Cleaner & Hyperlink Formatter
# ==========================================

def clean_drag_and_drop_path(raw_input: str) -> str:
    """Sanitizes file paths dragged into macOS, Windows, and Linux terminals."""
    cleaned = raw_input.strip()
    # Remove leading and trailing quotation marks added by terminal emulators
    if (cleaned.startswith("'") and cleaned.endswith("'")) or (cleaned.startswith('"') and cleaned.endswith('"')):
        cleaned = cleaned[1:-1]
    # Handle escaped spaces from POSIX terminals (e.g., /Path\ With\ Spaces.pdf)
    cleaned = cleaned.replace("\\ ", " ")
    # Handle file:// URI scheme drops
    if cleaned.startswith("file://"):
        parsed_url = urllib.parse.urlparse(cleaned)
        cleaned = urllib.parse.unquote(parsed_url.path)
        if sys.platform.startswith("win") and cleaned.startswith("/"):
            cleaned = cleaned[1:]
    return os.path.abspath(cleaned)


def create_terminal_hyperlink(file_path: str, display_text: str = None) -> str:
    """Generates an ANSI/OSC 8 clickable hyperlink supported in modern terminals."""
    display = display_text if display_text else file_path
    abs_path = os.path.abspath(file_path)
    file_url = Path(abs_path).as_uri()
    # OSC 8 escape sequence: \033]8;;URI\033\TEXT\033]8;;\033\
    return f"\033]8;;{file_url}\033\\{display}\033]8;;\033\\"


def get_default_downloads_folder() -> Path:
    """Resolves standard Downloads directory across macOS, Windows, and Linux."""
    return Path.home() / "Downloads"


# ==========================================
# 4. Processing Pipeline
# ==========================================

def process_file_pipeline(file_path: str):
    print(f"\n[*] Reading document: {file_path}")
    raw_text = load_document_text(file_path)
    print(f"[*] Extracted {len(raw_text):,} characters.")

    chunks = chunk_text(raw_text)
    print(f"[*] Segmented into {len(chunks)} chunk(s). Processing with DeepSeek...")

    all_items = []
    seen_keys = set()

    for idx, chunk in enumerate(chunks):
        print(f"  -> Structuring chunk {idx + 1}/{len(chunks)}...")
        extracted = extract_entities_with_llm(chunk)
        for item in extracted:
            cat = str(item.get("category", "")).lower().strip()
            key = str(item.get("key", "")).lower().strip()
            if cat in ["team", "projects", "jargon"] and key:
                dedup_key = (cat, key)
                if dedup_key not in seen_keys:
                    seen_keys.add(dedup_key)
                    all_items.append(item)

    print(f"[*] Found {len(all_items)} unique structured entities.")

    # Target save location: ~/Downloads
    downloads_dir = get_default_downloads_folder()
    downloads_dir.mkdir(parents=True, exist_ok=True)
    
    stem = Path(file_path).stem
    safe_stem = re.sub(r'[^a-zA-Z0-9_-]', '_', stem)
    output_filename = f"echo_knowledge_{safe_stem}.json"
    output_path = downloads_dir / output_filename

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"items": all_items}, f, indent=2, ensure_ascii=False)

    upsert_to_supabase(all_items)

    # Clickable terminal hyperlink output
    clickable_link = create_terminal_hyperlink(str(output_path), display_text=str(output_path))
    print("\n[✓] Ingestion Complete!")
    print(f"[*] File saved to: {clickable_link}")
    print("    (Hold Cmd/Ctrl and click the link above to open)\n")


# ==========================================
# 5. Interactive Terminal Loop
# ==========================================

def main():
    print("=" * 65)
    print("  PROJECT ECHO — UNIVERSAL DOCUMENT KNOWLEDGE INGESTION")
    print("=" * 65)
    print("Supported Formats: PDF, DOCX, PPTX, XLSX, XLS, CSV, TXT, MD")
    print("Type 'exit' or press Ctrl+C to quit.\n")

    while True:
        try:
            user_input = input("Drag and drop your file here: ").strip()
            
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "q"]:
                print("Exiting.")
                break

            target_path = clean_drag_and_drop_path(user_input)

            if not os.path.isfile(target_path):
                print(f"[!] Error: Could not locate file at: {target_path}\n")
                continue

            process_file_pipeline(target_path)

        except KeyboardInterrupt:
            print("\nExiting.")
            break
        except Exception as e:
            print(f"[!] Pipeline Error: {e}\n")


if __name__ == "__main__":
    main()
