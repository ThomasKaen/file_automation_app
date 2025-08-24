from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass
class JobResult:
    src: Path
    dst: Path
    ok: bool
    reason: Optional[str] = None

@dataclass(frozen=True)
class SortOptions:
    mode: str = "by_ext" #by ext, type, month
    recursive: bool = True
    copy_mode: bool = True
    dst_root: Optional[Path] = None

@dataclass(frozen=True)
class RenameOptions:
    prefix: str = ""
    suffix: str = ""
    numbering: bool = False
    start_num = 1
    find_pat: str = ""
    replace_with: str = ""
    recursive: bool = True
    filter_exts: str = "*"