import os
import hashlib
from pathlib import Path
from typing import Tuple
from backend.core.supabase_client import get_supabase_client
from backend.core.config import settings

MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024  # 15 MB
STORAGE_BASE_DIR = Path("backend/storage/documents")
DEFAULT_BUCKET = getattr(settings, "SUPABASE_BUCKET", "mandap-documents") or "mandap-documents"

def validate_pdf(file_bytes: bytes, filename: str) -> None:
    if not filename.lower().endswith(".pdf"):
        raise ValueError("Invalid file format. Only PDF documents (.pdf) are permitted.")
    if len(file_bytes) == 0:
        raise ValueError("Uploaded file is empty.")
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise ValueError("File size exceeds 15 MB maximum limit.")
    if not file_bytes.startswith(b"%PDF"):
        raise ValueError("Invalid PDF header signature. File is corrupted or not a valid PDF.")

def calculate_sha256(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()

def save_document_file(wedding_id: str, doc_id: str, filename: str, file_bytes: bytes) -> str:
    validate_pdf(file_bytes, filename)
    supabase = get_supabase_client()
    safe_filename = "".join(c for c in filename if c.isalnum() or c in "._- ")

    if supabase:
        try:
            bucket = getattr(settings, "SUPABASE_BUCKET", DEFAULT_BUCKET) or DEFAULT_BUCKET
            storage_key = f"{wedding_id}/{doc_id}_{safe_filename}"
            supabase.storage.from_(bucket).upload(storage_key, file_bytes, {"content-type": "application/pdf"})
            return f"supabase://{bucket}/{storage_key}"
        except Exception:
            pass  # Fallback to local storage

    # Local filesystem storage
    wedding_dir = STORAGE_BASE_DIR / wedding_id
    wedding_dir.mkdir(parents=True, exist_ok=True)
    local_path = wedding_dir / f"{doc_id}_{safe_filename}"
    with open(local_path, "wb") as f:
        f.write(file_bytes)

    return str(local_path.as_posix())

def read_document_file(storage_path: str) -> bytes:
    if storage_path.startswith("supabase://"):
        supabase = get_supabase_client()
        if supabase:
            bucket, key = storage_path.replace("supabase://", "").split("/", 1)
            return supabase.storage.from_(bucket).download(key)
    # Local filesystem
    target_path = Path(storage_path)
    if not target_path.is_file():
        # Fallback candidate checks
        cand1 = Path("backend/storage") / storage_path
        if cand1.is_file():
            target_path = cand1
        else:
            cand2 = Path("backend") / storage_path
            if cand2.is_file():
                target_path = cand2
            else:
                cand3 = Path("backend/storage/documents") / Path(storage_path).name
                if cand3.is_file():
                    target_path = cand3
    with open(target_path, "rb") as f:
        return f.read()
