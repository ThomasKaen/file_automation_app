import os
import re
import shutil
import threading
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from ..core.io_utils import ensure_unique, file_category, iter_files


class FileAutomationApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("File Automation App - Sorter + Bulk Renamer")
        self.geometry("900x560")

        nb = ttk.Notebook(self)
        self.sort_tab = SortTab(nb)
        self.rename_tab = RenameTab(nb)
        nb.add(self.sort_tab, text="Sorter")
        nb.add(self.rename_tab, text="Bulk Renamer")
        nb.pack(fill="both", expand=True)

        # unified log
        self.log = tk.Text(self, height=8, wrap="none")
        self.log.pack(fill="both", expand=False, padx=10, pady=(0,10))
        self.status = tk.StringVar(value="Ready")
        ttk.Label(self, textvariable=self.status, anchor="w").pack(fill="x", padx=10, pady=(0,10))

        # hook tabs to use shared log/status
        self.sort_tab.bind_logger(self._log, self._set_status)
        self.rename_tab.bind_logger(self._log, self._set_status)

    def _log(self, msg: str):
        self.log.insert("end", msg.strip() + "\n")
        self.log.see("end")
        self.update_idletasks()

    def _set_status(self, text: str):
        self.status.set(text)
        self.update_idletasks()

# --- Sorter Tab --- #
class SortTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Inputs
        frm = ttk.LabelFrame(self, text="Inputs")
        frm.pack(fill="x", padx=10, pady=10)
        self.src_dir = tk.StringVar()
        self.dst_dir = tk.StringVar()
        self.recursive = tk.BooleanVar(value=True)
        self.copy_mode = tk.BooleanVar(value=True)  # safer default
        self.mode = tk.StringVar(value="by_ext")  # by_ext | by_type | by_month

        row1 = ttk.Frame(frm);
        row1.pack(fill="x", pady=3)
        ttk.Label(row1, text="Source folder:").pack(side="left")
        ttk.Entry(row1, textvariable=self.src_dir, width=70).pack(side="left", padx=6)
        ttk.Button(row1, text="Browse", command=self._pick_src).pack(side="left")

        row2 = ttk.Frame(frm);
        row2.pack(fill="x", pady=3)
        ttk.Label(row2, text="Destination:").pack(side="left")
        ttk.Entry(row2, textvariable=self.dst_dir, width=70).pack(side="left", padx=6)
        ttk.Button(row2, text="Browse", command=self._pick_dst).pack(side="left")
        ttk.Label(row2, text="(Empty → will create 'sorted_output' next to source)").pack(side="left", padx=6)

        row3 = ttk.Frame(frm);
        row3.pack(fill="x", pady=3)
        ttk.Label(row3, text="Mode:").pack(side="left")
        ttk.Radiobutton(row3, text="By extension", variable=self.mode, value="by_ext").pack(side="left", padx=6)
        ttk.Radiobutton(row3, text="By file type", variable=self.mode, value="by_type").pack(side="left", padx=6)
        ttk.Radiobutton(row3, text="By modified month (YYYY-MM)", variable=self.mode, value="by_month").pack(
            side="left", padx=6)

        row4 = ttk.Frame(frm);
        row4.pack(fill="x", pady=3)
        ttk.Checkbutton(row4, text="Include subfolders", variable=self.recursive).pack(side="left")
        ttk.Checkbutton(row4, text="Copy files (instead of move)", variable=self.copy_mode).pack(side="left", padx=12)

        # Actions
        act = ttk.Frame(self);
        act.pack(fill="x", padx=10, pady=(0, 8))
        ttk.Button(act, text="Preview", command=self.preview).pack(side="left")
        ttk.Button(act, text="Apply Sort", command=self.apply).pack(side="left", padx=8)

        # Preview box
        self.preview_box = tk.Text(self, height=14, wrap="none")
        self.preview_box.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self._logger = None
        self._status = None

    def bind_logger(self, logger, set_status):
        self._logger = logger
        self._status = set_status

    def _log(self, msg):
        if self._logger: self._logger(msg)

    def _status_set(self, s):
        if self._status: self._status(s)

    def _pick_src(self):
        p = filedialog.askdirectory(title="Select source folder")
        if p: self.src_dir.set(p)

    def _pick_dst(self):
        p = filedialog.askdirectory(title="Select destination folder")
        if p: self.dst_dir.set(p)

    def _plan(self):
        src = Path(self.src_dir.get().strip() or "")
        if not src.is_dir():
            messagebox.showwarning("Missing", "Please choose a source folder")
            return None

        dst_root = Path(self.dst_dir.get().strip())
        if not dst_root:
            dst_root = src.parent / "sorted output"

        mode = self.mode.get()
        recursive = self.recursive.get()
        copy_mode = self.copy_mode.get()

        plans = []
        for p in iter_files(src, recursive):
            try:
                if mode == "by_ext":
                    sub = (p.suffix.lower() or ".noext").lstrip(".")
                elif mode == "by_type":
                    sub = file_category(p)
                else: #by_month
                    ts = datetime.fromtimestamp(p.stat().st_mtime)
                    sub = ts.strftime("%Y-%m")
                out_dir = dst_root / sub
                out_dir.mkdir(parents=True, exist_ok=True)
                dst = ensure_unique(out_dir / p.name)
                plans.append((p, dst, copy_mode))
            except Exception as e:
                self._log(f"[skip] {p} -> {e}")
        return plans, dst_root

    def preview(self):
        res = self._plan()
        if not res: return
        plans, dst_root = res
        self.preview_box.delete("1.0", "end")
        self.preview_box.insert("end", f"Planned operations: {len(plans)}\nDestination folder: {dst_root}\n\n")
        for i, (src, dst, copy_mode) in enumerate(plans[:300], start=1):
            op = "COPY" if copy_mode else "MOVE"
            self.preview_box.insert("end", f"{i:>4}. [{op}] {src} -> {dst}\n")
        if len(plans) > 300:
            self.preview_box.insert("end", f"...and {len(plans)-300} more\n")
        self._status_set("Preview ready.")

    def apply(self):
        res = self._plan()
        if not res: return
        plans, dst_root = res

        def worker():
            done = 0
            for src, dst, copy_mode in plans:
                try:
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    if copy_mode:
                        shutil.copy2(src, dst)
                    else:
                        shutil.move(str(src), str(dst))
                        done += 1
                except Exception as e:
                    self._log(f"[error] {src} -> {e}")
            self._status_set(f"Sorting done. {done}/{len(plans)} succeeded. Output folder: {dst_root}")

        threading.Thread(target=worker, daemon=True).start()
        self._status_set("Running...")

class RenameTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        frm = ttk.LabelFrame(self, text="Inputs")
        frm.pack(fill="x", padx=10, pady=10)
        self.root_dir = tk.StringVar()
        self.recursive = tk.BooleanVar(value=True)
        self.filter_exts = tk.StringVar(value="*")  # e.g. *.jpg;*.png or *

        row1 = ttk.Frame(frm); row1.pack(fill="x", pady=3)
        ttk.Label(row1, text="Target folder:").pack(side="left")
        ttk.Entry(row1, textvariable=self.root_dir, width=70).pack(side="left", padx=6)
        ttk.Button(row1, text="Browse", command=self._pick_root).pack(side="left")

        row2 = ttk.Frame(frm); row2.pack(fill="x", pady=3)
        ttk.Checkbutton(row2, text="Include subfolders", variable=self.recursive).pack(side="left")
        ttk.Label(row2, text="Filter:").pack(side="left", padx=(18,0))
        ttk.Entry(row2, textvariable=self.filter_exts, width=20).pack(side="left", padx=6)
        ttk.Label(row2, text="(* or patterns like *.jpg;*.png)").pack(side="left")

        opt = ttk.LabelFrame(self, text="Rename Rules")
        opt.pack(fill="x", padx=10, pady=6)
        self.prefix = tk.StringVar(value="")
        self.suffix = tk.StringVar(value="")
        self.numbering = tk.BooleanVar(value=False)
        self.start_num = tk.IntVar(value=1)
        self.find_pat = tk.StringVar(value="")
        self.replace_with = tk.StringVar(value="")

        r1 = ttk.Frame(opt); r1.pack(fill="x", pady=3)
        ttk.Label(r1, text="Prefix:").pack(side="left")
        ttk.Entry(r1, textvariable=self.prefix, width=20).pack(side="left", padx=6)
        ttk.Label(r1, text="Suffix:").pack(side="left")
        ttk.Entry(r1, textvariable=self.suffix, width=20).pack(side="left", padx=6)

        r2 = ttk.Frame(opt); r2.pack(fill="x", pady=3)
        ttk.Checkbutton(r2, text="Add numbering", variable=self.numbering).pack(side="left")
        ttk.Label(r2, text="Start at:").pack(side="left", padx=(10,0))
        ttk.Spinbox(r2, from_=0, to=999999, textvariable=self.start_num, width=7).pack(side="left", padx=6)

        r3 = ttk.Frame(opt); r3.pack(fill="x", pady=3)
        ttk.Label(r3, text="Find:").pack(side="left")
        ttk.Entry(r3, textvariable=self.find_pat, width=20).pack(side="left", padx=6)
        ttk.Label(r3, text="Replace with:").pack(side="left")
        ttk.Entry(r3, textvariable=self.replace_with, width=20).pack(side="left", padx=6)
        ttk.Label(r3, text="(regex supported)").pack(side="left", padx=6)

        act = ttk.Frame(self); act.pack(fill="x", padx=10, pady=(0,8))
        ttk.Button(act, text="Preview", command=self.preview).pack(side="left")
        ttk.Button(act, text="Apply Rename", command=self.apply).pack(side="left", padx=8)

        self.preview_box = tk.Text(self, height=14, wrap="none")
        self.preview_box.pack(fill="both", expand=True, padx=10, pady=(0,10))

        self._logger = None
        self._status = None

    def bind_logger(self, logger, set_status):
        self._logger = logger
        self._status = set_status

    def _log(self, msg):
        if self._logger: self._logger(msg)

    def _status_set(self, s):
        if self._status: self._status(s)

    def _pick_root(self):
        p = filedialog.askdirectory(title="Select folder to rename files in")
        if p: self.root_dir.set(p)

    def _match_filter(self, p: Path) -> bool:
        pat = self.filter_exts.get().strip()
        if pat == "*" or pat == "":
            return True
        # support semicolon-separated glob patterns like *.jpg;*.png
        pats = [x.strip() for x in pat.split(";") if x.strip()]
        name = p.name.lower()
        for g in pats:
            # simple glob -> regex
            rgx = re.escape(g.lower()).replace(r"\*", ".*").replace(r"\?", ".")
            if re.fullmatch(rgx, name):
                return True
        return False

    def _plan(self):
        root = Path(self.root_dir.get().strip() or "")
        if not root.is_dir():
            messagebox.showwarning("Missing", "Please choose a target folder.")
            return None
        recursive = self.recursive.get()

        files = [p for p in iter_files(root, recursive) if self._match_filter(p)]
        plans = []

        n = self.start_num.get()
        for p in files:
            stem, ext = p.stem, p.suffix
            new_stem = stem

            # find/replace (regex)
            fp = self.find_pat.get()
            if fp:
                try:
                    new_stem = re.sub(fp, self.replace_with.get(), new_stem)
                except re.error as e:
                    messagebox.showerror("Regex error", f"Invalid 'Find' pattern:\n{e}")
                    return None

            # prefix/suffix
            new_stem = f"{self.prefix.get()}{new_stem}{self.suffix.get()}"

            # numbering
            if self.numbering.get():
                new_stem = f"{new_stem}_{n:03d}"
                n += 1

            dst = ensure_unique(p.with_name(new_stem + ext))
            if dst != p:
                plans.append((p, dst))

        return plans

    def preview(self):
        plans = self._plan()
        if plans is None: return
        self.preview_box.delete("1.0", "end")
        self.preview_box.insert("end", f"Planned renames: {len(plans)}\n\n")
        for i, (src, dst) in enumerate(plans[:300], start=1):
            self.preview_box.insert("end", f"{i:>4}. {src.name}  →  {dst.name}\n")
        if len(plans) > 300:
            self.preview_box.insert("end", f"...and {len(plans)-300} more\n")
        self._status_set("Preview ready.")

    def apply(self):
        plans = self._plan()
        if plans is None: return

        def worker():
            done = 0
            for src, dst in plans:
                try:
                    os.replace(src, dst)
                    done += 1
                except Exception as e:
                    self._log(f"[error] {src} -> {e}")
            self._status_set(f"Renaming done. {done}/{len(plans)} succeeded.")

        threading.Thread(target=worker, daemon=True).start()
        self._status_set("Running…")

# -----------------------
# Run
# -----------------------

if __name__ == "__main__":
    FileAutomationApp().mainloop()