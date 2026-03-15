"""
gui.py  —  Local File Intelligence System
Compatible with flet >= 0.80
"""
import datetime
import os
import threading

import flet as ft

from scanner import get_all_files
from analyzer import find_duplicates, get_storage_by_extension, delete_files, get_top_large_files
from organizer import organize_folder, get_organize_plan


# ── Palette ────────────────────────────────────────────────────────────────────
BG     = "#0F1115"
SURF   = "#1A1D24"
SURF2  = "#252A34"
BORDER = "#2E3440"
CYAN   = "#00BCD4"
GREEN  = "#4CAF50"
YELLOW = "#FFC107"
RED    = "#F44336"
TEXT   = "#ECEFF4"
DIM    = "#7B8BA0"
WHITE  = "#FFFFFF"


class FileIntelApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.all_files: list = []
        self.detected_dupes: list = []
        self.target_path: str = ""
        self.stop_event = threading.Event()

        # ── Page setup ────────────────────────────────────────────────────────
        page.title         = "Local File Intelligence System"
        page.theme_mode    = ft.ThemeMode.DARK
        page.bgcolor       = BG
        page.window.width  = 1100
        page.window.height = 900
        page.padding       = 30
        page.scroll        = ft.ScrollMode.ADAPTIVE

        # ── Path input ────────────────────────────────────────────────────────
        self.path_input = ft.TextField(
            label="Enter folder path",
            expand=True,
            border_radius=12,
            border_color=CYAN,
            focused_border_color=CYAN,
            prefix_icon=ft.Icons.FOLDER_OPEN,
            text_size=14,
            color=TEXT,
            bgcolor=SURF2,
            cursor_color=CYAN,
            label_style=ft.TextStyle(color=DIM),
        )

        # ── Progress bar (no IconButton — just text cancel) ───────────────────
        self.progress_bar  = ft.ProgressBar(
            width=400, color=CYAN, bgcolor=SURF2, visible=False,
        )
        self.progress_text = ft.Text("", size=12, color=CYAN, weight=ft.FontWeight.BOLD)
        self.cancel_btn    = ft.Button(
            content="STOP",
            visible=False,
            on_click=self._cancel,
            style=ft.ButtonStyle(
                color=WHITE,
                bgcolor=RED,
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
        )

        # ── Dashboard (stat cards + top files) ───────────────────────────────
        self.stat_cards   = ft.Row(spacing=15, wrap=True)
        self.top_files    = ft.Column(spacing=8)

        self.dashboard = ft.Column([
            ft.Text("STORAGE REPORT", size=14, weight=ft.FontWeight.BOLD, color=CYAN),
            self.stat_cards,
            ft.Divider(height=30, color="transparent"),
            ft.Text("TOP 5 LARGEST FILES", size=14, weight=ft.FontWeight.BOLD, color=CYAN),
            self.top_files,
            ft.Divider(height=20, color="transparent"),
        ], visible=False)

        # ── Duplicate results ─────────────────────────────────────────────────
        self.dupe_col     = ft.Column(spacing=6)
        self.dupe_section = ft.Column([
            ft.Divider(height=20, color="transparent"),
            ft.Text("DUPLICATE FILES FOUND", size=14, weight=ft.FontWeight.BOLD, color=YELLOW),
            ft.Container(height=8),
            self.dupe_col,
        ], visible=False)

        # ── Log ───────────────────────────────────────────────────────────────
        self.log_view = ft.ListView(
            expand=True, spacing=2, auto_scroll=True,
        )

        self._build_ui()

    # ── Layout ─────────────────────────────────────────────────────────────────
    def _build_ui(self):
        def _btn(label, icon, handler, color=CYAN, bg=SURF2):
            return ft.Button(
                content=label,
                icon=icon,
                on_click=handler,
                style=ft.ButtonStyle(
                    color=color,
                    bgcolor=bg,
                    shape=ft.RoundedRectangleBorder(radius=10),
                ),
            )

        btns = ft.Row([
            _btn("SCAN SYSTEM",  ft.Icons.SEARCH,        self._on_scan),
            _btn("FIND DUPES",   ft.Icons.COPY_ALL,       self._on_dupes),
            _btn("ORGANIZE",     ft.Icons.AUTO_AWESOME,   self._on_organize,  GREEN,  "#1A2E1A"),
            _btn("WIPE DUPES",   ft.Icons.DELETE_SWEEP,   self._on_wipe,      RED,    "#2E1A1A"),
        ], spacing=15, wrap=True)

        self.page.add(
            # Header
            ft.Row([
                ft.Icon(ft.Icons.SATELLITE_ALT, color=CYAN, size=35),
                ft.Column([
                    ft.Text("LOCAL FILE INTELLIGENCE",
                            size=26, weight=ft.FontWeight.BOLD, color=WHITE),
                    ft.Text("Scan · Deduplicate · Organize",
                            size=11, color=DIM, italic=True),
                ], spacing=2),
            ], spacing=12),

            ft.Container(height=16),

            # Path row
            ft.Row([self.path_input], spacing=0),

            ft.Container(height=12),

            # Action buttons
            btns,

            # Progress row
            ft.Row([
                self.progress_bar,
                self.progress_text,
                self.cancel_btn,
            ], spacing=15),

            ft.Divider(color=SURF2, height=30),

            # Dashboard (stat cards + top files)
            self.dashboard,

            # Duplicate section
            self.dupe_section,

            # Log
            ft.Text("ACTIVITY LOG", size=12, color=DIM, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=self.log_view,
                height=250,
                bgcolor=SURF,
                border_radius=15,
                padding=15,
                border=ft.Border.all(1, BORDER),
            ),
            ft.Container(height=20),
        )

    # ── Helpers ────────────────────────────────────────────────────────────────
    def _log(self, msg, color=DIM):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_view.controls.append(
            ft.Text(f"[{now}] {msg}", size=11,
                    font_family="monospace", color=color, selectable=True)
        )
        if len(self.log_view.controls) > 300:
            self.log_view.controls.pop(0)
        self.page.update()

    def _cancel(self, e):
        self.stop_event.set()
        self.cancel_btn.disabled = True
        self._log("⛔ Abort signal sent…", RED)

    def _busy(self, on: bool, label=""):
        self.progress_bar.visible  = on
        self.cancel_btn.visible    = on
        self.cancel_btn.disabled   = False
        self.progress_text.value   = label if on else ""
        if not on:
            self.progress_bar.value = None
        self.page.update()

    def _set_progress(self, curr, total, name):
        self.progress_bar.value  = curr / total
        self.progress_text.value = f"[{curr}/{total}] {name[:30]}…"
        self.page.update()

    # ── SCAN ───────────────────────────────────────────────────────────────────
    def _on_scan(self, e):
        path = self.path_input.value.strip()
        if not path or not os.path.isdir(path):
            self._log("ERROR: Invalid path.", RED)
            return
        self.target_path = path
        self.stop_event.clear()
        self._busy(True, f"Scanning {path}…")
        threading.Thread(target=self._do_scan, daemon=True).start()

    def _do_scan(self):
        self._log(f"Scanning: {self.target_path}", CYAN)
        self.all_files = get_all_files(self.target_path)

        if self.stop_event.is_set():
            self._log("Scan cancelled.", RED)
            self._busy(False)
            return

        # ── Stat cards: one card per extension ───────────────────────────────
        stats = get_storage_by_extension(self.all_files)
        self.stat_cards.controls.clear()
        for ext, size in sorted(stats.items(), key=lambda x: x[1], reverse=True):
            label   = ext.upper() if ext else "UNKNOWN"
            size_mb = round(size / 1_048_576, 2)
            count   = sum(1 for f in self.all_files if f["ext"] == ext)
            self.stat_cards.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(label, size=11, color=CYAN,
                                weight=ft.FontWeight.BOLD),
                        ft.Text(f"{size_mb} MB", size=18,
                                weight=ft.FontWeight.BOLD, color=WHITE),
                        ft.Text(f"{count} file(s)", size=10, color=DIM),
                    ], spacing=3),
                    bgcolor=SURF,
                    padding=ft.padding.all(16),
                    border_radius=15,
                    width=150,
                    border=ft.Border.all(1, BORDER),
                )
            )

        # ── Top 5 largest ────────────────────────────────────────────────────
        top = get_top_large_files(self.all_files, count=5)
        self.top_files.controls.clear()
        max_sz = top[0]["size"] if top else 1
        for i, f in enumerate(top, 1):
            mb  = round(f["size"] / 1_048_576, 2)
            pct = f["size"] / max_sz
            self.top_files.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(f"{i}.", size=12, color=CYAN,
                                    weight=ft.FontWeight.BOLD, width=24),
                            ft.Text(f["name"], expand=True, size=13,
                                    color=TEXT, no_wrap=True,
                                    overflow=ft.TextOverflow.ELLIPSIS),
                            ft.Text(f"{mb} MB", color=CYAN, size=12,
                                    weight=ft.FontWeight.BOLD),
                        ], spacing=8),
                        ft.ProgressBar(value=pct, color=CYAN,
                                       bgcolor=BORDER, height=4),
                    ], spacing=4),
                    bgcolor=SURF,
                    padding=ft.padding.all(14),
                    border_radius=10,
                    border=ft.Border.all(1, BORDER),
                )
            )

        self.dashboard.visible = True
        self._busy(False)
        self._log(f"✓ Scan complete — {len(self.all_files)} files indexed.", GREEN)

    # ── FIND DUPES ─────────────────────────────────────────────────────────────
    def _on_dupes(self, e):
        if not self.all_files:
            self._log("Run SCAN SYSTEM first.", YELLOW)
            return
        self.stop_event.clear()
        self.dupe_section.visible = False
        self.dupe_col.controls.clear()
        self.page.update()
        self._busy(True, "Hashing files…")
        threading.Thread(target=self._do_dupes, daemon=True).start()

    def _do_dupes(self):
        self._log("Comparing file hashes…", CYAN)
        self.detected_dupes = find_duplicates(
            self.all_files,
            progress_callback=self._set_progress,
            stop_event=self.stop_event,
        )

        if self.stop_event.is_set():
            self._log("Duplicate scan cancelled.", RED)
            self._busy(False)
            return

        if not self.detected_dupes:
            self._log("✓ No duplicates found — folder is clean.", GREEN)
            self._busy(False)
            return

        wasted = 0
        self.dupe_col.controls.clear()
        for orig, dupe in self.detected_dupes:
            try:
                sz = os.path.getsize(dupe)
            except Exception:
                sz = 0
            wasted += sz
            self.dupe_col.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Container(
                                content=ft.Text("ORIGINAL", size=10,
                                                color=GREEN,
                                                weight=ft.FontWeight.BOLD),
                                bgcolor="#1A2E1A", border_radius=6,
                                padding=ft.padding.symmetric(horizontal=8, vertical=3),
                            ),
                            ft.Text(orig, size=11, color=DIM, expand=True,
                                    selectable=True, no_wrap=True,
                                    overflow=ft.TextOverflow.ELLIPSIS),
                        ], spacing=8),
                        ft.Row([
                            ft.Container(
                                content=ft.Text("DUPLICATE", size=10,
                                                color=RED,
                                                weight=ft.FontWeight.BOLD),
                                bgcolor="#2E1A1A", border_radius=6,
                                padding=ft.padding.symmetric(horizontal=8, vertical=3),
                            ),
                            ft.Text(dupe, size=11, color=TEXT, expand=True,
                                    selectable=True, no_wrap=True,
                                    overflow=ft.TextOverflow.ELLIPSIS),
                            ft.Text(f"{round(sz/1_048_576, 2)} MB",
                                    size=11, color=RED, width=70),
                        ], spacing=8),
                    ], spacing=6),
                    bgcolor=SURF, padding=ft.padding.all(12),
                    border_radius=10, border=ft.Border.all(1, BORDER),
                )
            )

        self._log(
            f"⚠ {len(self.detected_dupes)} pair(s) — "
            f"{round(wasted/1_048_576, 2)} MB wasted.", YELLOW,
        )
        self.dupe_section.visible = True
        self._busy(False)

    # ── ORGANIZE ───────────────────────────────────────────────────────────────
    def _on_organize(self, e):
        if not self.target_path:
            self._log("Run SCAN SYSTEM first.", YELLOW)
            return
        plan = get_organize_plan(self.target_path)
        if not plan:
            self._log("No loose files to organize.", DIM)
            return

        # Group by destination
        groups: dict = {}
        for fname, dest in plan:
            groups.setdefault(dest, []).append(fname)

        # Build preview rows
        preview_rows = []
        for dest, files in sorted(groups.items()):
            preview_rows.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.FOLDER, color=CYAN, size=16),
                            ft.Text(f"{dest}/", size=12, color=CYAN,
                                    weight=ft.FontWeight.BOLD),
                            ft.Container(
                                content=ft.Text(f"{len(files)} files", size=10,
                                                color=CYAN, weight=ft.FontWeight.BOLD),
                                bgcolor=SURF2, border_radius=6,
                                padding=ft.padding.symmetric(horizontal=8, vertical=3),
                            ),
                        ], spacing=8),
                        ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.ARROW_RIGHT, color=DIM, size=14),
                                ft.Text(fn, size=11, color=DIM, expand=True,
                                        no_wrap=True,
                                        overflow=ft.TextOverflow.ELLIPSIS),
                            ], spacing=4)
                            for fn in files[:10]
                        ] + ([ft.Text(f"  …and {len(files)-10} more",
                                      size=10, color=DIM, italic=True)]
                             if len(files) > 10 else []),
                        spacing=2),
                    ], spacing=6),
                    bgcolor=SURF2, border_radius=10, padding=ft.padding.all(12),
                    border=ft.Border.all(1, BORDER),
                    margin=ft.Margin(0, 0, 0, 8),
                )
            )

        def do_run(_):
            page.pop_dialog()
            self._busy(True, "Organizing files…")
            threading.Thread(target=self._do_organize, daemon=True).start()

        page = self.page
        dlg = ft.AlertDialog(
            modal=True, bgcolor=SURF,
            title=ft.Text("ORGANIZE PREVIEW",
                          weight=ft.FontWeight.BOLD, color=WHITE, size=16),
            content=ft.Column([
                ft.Text(f"{len(plan)} file(s) will be moved into sub-folders:",
                        size=12, color=DIM),
                ft.Container(height=8),
                ft.Container(
                    content=ft.Column(preview_rows,
                                      scroll=ft.ScrollMode.ADAPTIVE, spacing=0),
                    height=340, bgcolor=BG,
                    border_radius=10, padding=ft.padding.all(10),
                    border=ft.Border.all(1, BORDER),
                ),
            ], tight=True, width=540),
            actions=[
                ft.Button(
                    content="CANCEL",
                    on_click=lambda _: page.pop_dialog(),
                    style=ft.ButtonStyle(
                        color=DIM, bgcolor=SURF2,
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                ),
                ft.Button(
                    content="RUN — MOVE FILES",
                    icon=ft.Icons.PLAY_ARROW,
                    on_click=do_run,
                    style=ft.ButtonStyle(
                        color=WHITE, bgcolor=GREEN,
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.show_dialog(dlg)

    def _do_organize(self):
        self._log("Moving files into sub-folders…", CYAN)
        count = organize_folder(self.target_path, dry_run=False)
        self._log(f"✓ Done — {count} file(s) moved.", GREEN)
        self._log("Refreshing index…", DIM)
        self._do_scan()

    # ── WIPE DUPES ─────────────────────────────────────────────────────────────
    def _on_wipe(self, e):
        if not self.detected_dupes:
            self._log("No duplicates queued — run FIND DUPES first.", YELLOW)
            return

        n    = len(self.detected_dupes)
        page = self.page

        def confirm(_):
            page.pop_dialog()
            deleted = delete_files([p[1] for p in self.detected_dupes])
            self.detected_dupes = []
            self.dupe_col.controls.clear()
            self.dupe_section.visible = False
            self._log(f"✕ {deleted} file(s) permanently deleted.", RED)
            threading.Thread(target=self._do_scan, daemon=True).start()

        dlg = ft.AlertDialog(
            modal=True, bgcolor=SURF,
            title=ft.Text("CONFIRM DELETION",
                          weight=ft.FontWeight.BOLD, color=RED, size=15),
            content=ft.Text(
                f"You are about to permanently delete {n} duplicate file(s).\n"
                "This action CANNOT be undone.",
                size=13, color=TEXT,
            ),
            actions=[
                ft.Button(
                    content="CANCEL",
                    on_click=lambda _: page.pop_dialog(),
                    style=ft.ButtonStyle(
                        color=DIM, bgcolor=SURF2,
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                ),
                ft.Button(
                    content=f"DELETE {n} FILES",
                    icon=ft.Icons.DELETE_FOREVER,
                    on_click=confirm,
                    style=ft.ButtonStyle(
                        color=WHITE, bgcolor=RED,
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.show_dialog(dlg)


# ── Entry ──────────────────────────────────────────────────────────────────────
def main(page: ft.Page):
    FileIntelApp(page)


ft.run(main)