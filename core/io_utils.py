import os, re
from pathlib import Path
from datetime import datetime

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tiff"}
VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv", ".mpeg", ".mpg"}
AUDIO_EXTS = {".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a"}
DOC_EXTS   = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".csv", ".md", ".rtf"}
ARCH_EXTS  = {".zip", ".rar", ".7z", ".tar", ".gz"}

def file_category(p: Path) -> str:
    ext = p.suffix.lower()
    if ext in IMAGE_EXTS: return "Images"
    if ext in VIDEO_EXTS: return "Videos"
    if ext in AUDIO_EXTS: return "Audio"
    if ext in DOC_EXTS: return "Documents"
    if ext in ARCH_EXTS: return "Archives"
    return "Other"

def iter_files(root: Path, recursive: bool):
    if recursive:
        yield from (p for p in root.rglob("*") if p.is_file())
    else:
        yield from (p for p in root.iterdir() if p.is_file())

def ensure_unique(dst: Path) -> Path:
    if not dst.exists(): return dst
    base = dst.with_suffix("")
    ext = dst.suffix
    n = 2
    while True:
        cand = Path(f"{base}_{n}{ext}")
        if not cand.exists(): return cand
        n += 1