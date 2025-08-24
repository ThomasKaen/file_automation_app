import os, re, shutil
from pathlib import Path
from datetime import datetime
from typing import List
from .models import JobResult, SortOptions, RenameOptions
from .io_utils import file_category, iter_files, ensure_unique

class SortService:
    def __init__(self, folder: Path):
        self.folder = folder

    def plan(self, opts: SortOptions) -> List[JobResult]:
        dst_root = opts.dst_root or (self.folder.parent / "sorted_output")
        results: List[JobResult] = []
        for p in iter_files(self.folder, opts.recursive):
            if opts.mode == "by_ext":
                sub = (p.suffix.lower() or ".noext").lstrip(".")
            elif opts.mode == "by_type":
                sub = file_category(p)
            else:
                ts = datetime.fromtimestamp(p.stat().st_mtime)
                sub = ts.strftime("%Y-%m")
            dst = ensure_unique(dst_root / sub / p.name)
            results.append(JobResult(p, dst, True))
        return results

    def execute(self, opts: SortOptions) -> List[JobResult]:
        plans = self.plan(opts)
        for r in plans:
            try:
                r.dst.parent.mkdir(parents=True, exist_ok=True)
                if opts.copy_mode:
                    shutil.copy2(r.src, r.dst)
                else:
                    shutil.move(str(r.src), str(r.dst))
            except Exception as e:
                r.ok = False
                r.reason = str(e)
        return plans

class RenameService:
    def __init__(self, folder: Path):
        self.folder = folder

    def plan(self, opts: RenameOptions) -> List[JobResult]:
        files = [p for p in iter_files(self.folder, opts.recursive)]
        plans: List[JobResult] = []
        n = opts.start_num
        for p in files:
            stem, ext = p.stem, p.suffix
            new_stem = stem
            if opts.find_pat:
                try:
                    new_stem = re.sub(opts.find_pat, opts.replace_with, new_stem)
                except re.error as e:
                    return [JobResult(p, p, False, f"Regex error: {e}")]
            new_stem = f"{opts.prefix}{new_stem}{opts.suffix}"
            if opts.numbering:
                new_stem = f"{new_stem}_{n:03d}"
                n += 1
            dst = ensure_unique(p.with_name(new_stem + ext))
            if dst != p:
                plans.append(JobResult(p, dst, True))
        return plans

    def execute(self, opts: RenameOptions) -> List[JobResult]:
        plans = self.plan(opts)
        for r in plans:
            try:
                os.replace(r.src, r.dst)
            except Exception as e:
                r.ok = False
                r.reason = str(e)
        return plans
