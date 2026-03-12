import flet as ft
import os
import threading
import datetime
from scanner import get_all_files
from analyzer import find_duplicates, get_storage_by_extension, delete_files, get_top_large_files
from organizer import organize_folder, get_organize_plan

class NexusApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.all_files = []
        self.detected_dupes = []
        self.target_path = ""
        # The key to stopping operations instantly
        self.stop_event = threading.Event()

        # System Theme
        self.page.title = "Nexus File Intelligence"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = "#0F1115"
        self.page.window_width = 1100
        self.page.window_height = 900
        self.page.padding = 30

        # UI Elements
        self.path_input = ft.TextField(
            label="SYSTEM PATH", expand=True, border_radius=12,
            border_color="cyan", focused_border_color="cyan",
            prefix_icon=ft.Icons.FOLDER_OPEN, text_size=14,
        )

        self.progress_bar = ft.ProgressBar(width=400, color="cyan", visible=False, bgcolor="#252A34")
        self.progress_text = ft.Text("", size=12, color="cyan", weight="bold")
        
        # New Annuler Button
        self.stop_btn = ft.ElevatedButton(
            "ANNULER", icon=ft.Icons.STOP_CIRCLE, color="white", bgcolor="#B22222",
            visible=False, on_click=self.cancel_task
        )

        self.stat_cards = ft.Row(spacing=15, scroll=ft.ScrollMode.ADAPTIVE)
        self.top_files_list = ft.Column(spacing=8)
        
        # Fixed Scrollable Log View
        self.log_view = ft.ListView(expand=True, spacing=2, auto_scroll=True)

        self.dashboard = ft.Column([
            ft.Text("STORAGE DISTRIBUTION", size=14, weight="bold", color="cyan"),
            self.stat_cards,
            ft.Divider(height=40, color="transparent"),
            ft.Text("TOP 5 HEAVY HITTERS", size=14, weight="bold", color="cyan"),
            self.top_files_list,
            ft.Divider(height=30, color="transparent"),
        ], visible=False)

        self.setup_ui()

    def setup_ui(self):
        btns = ft.Row([
            ft.ElevatedButton("SCAN SYSTEM", icon=ft.Icons.SEARCH, on_click=self.start_scan, 
                              style=ft.ButtonStyle(color="white", bgcolor="#252A34")),
            ft.ElevatedButton("FIND DUPES", icon=ft.Icons.COPY_ALL, on_click=self.start_dupe,
                              style=ft.ButtonStyle(color="white", bgcolor="#252A34")),
            ft.ElevatedButton("ORGANIZE", icon=ft.Icons.AUTO_AWESOME, on_click=self.show_org_menu,
                              style=ft.ButtonStyle(color="white", bgcolor="#252A34")),
            ft.ElevatedButton("WIPE DUPES", icon=ft.Icons.DELETE_SWEEP, on_click=self.clean_dupes, 
                              color="red", style=ft.ButtonStyle(bgcolor="#331111")),
        ], spacing=15)

        self.page.add(
            ft.Row([
                ft.Icon(ft.Icons.SATELLITE_ALT, color="cyan", size=35),
                ft.Column([
                    ft.Text("NEXUS CORE", size=28, weight="bold"),
                    ft.Text("ADVANCED FILE INTELLIGENCE SYSTEM", size=12, color="grey", italic=True),
                ], spacing=0)
            ]),
            ft.Container(height=10),
            ft.Row([self.path_input]),
            btns,
            ft.Row([self.progress_bar, self.progress_text, self.stop_btn], spacing=15),
            ft.Divider(color="#252A34", height=40),
            self.dashboard,
            ft.Text("ACTIVITY CONSOLE", size=12, color="grey", weight="bold"),
            ft.Container(
                content=self.log_view, height=250, bgcolor="#16191F",
                border_radius=15, padding=15, border=ft.Border.all(1, "#252A34")
            )
        )

    def log(self, msg):
        now = datetime.datetime.now().strftime('%H:%M:%S')
        self.log_view.controls.append(
            ft.Text(f"[{now}] {msg}", size=11, font_family="monospace", color="#A0AEC0")
        )
        self.page.update()

    def cancel_task(self, e):
        self.stop_event.set()
        self.log("ATTENTION: Manually stopping task. Cleaning up...")
        self.stop_btn.disabled = True
        self.page.update()

    def update_prog(self, curr, total, name):
        val = curr / total
        self.progress_bar.value = val
        # Tracking number added here (e.g. 15/100)
        self.progress_text.value = f"[{curr}/{total}] Analyzing: {name[:20]}..."
        self.page.update()

    def start_scan(self, e):
        path = self.path_input.value.strip()
        if not os.path.isdir(path):
            self.log("ERROR: Invalid Path.")
            return
        self.target_path = path
        self.stop_event.clear()
        threading.Thread(target=self.run_scan, daemon=True).start()

    def run_scan(self):
        self.progress_bar.visible = True
        self.log(f"Initiating scan on {self.target_path}")
        self.all_files = get_all_files(self.target_path)
        
        # Display Stats
        stats = get_storage_by_extension(self.all_files)
        self.stat_cards.controls.clear()
        for cat, size in stats.items():
            self.stat_cards.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(cat.upper(), size=10, color="cyan", weight="bold"),
                        ft.Text(f"{round(size/1e6, 2)} MB", size=18, weight="bold")
                    ], spacing=2),
                    bgcolor="#1E2229", padding=20, border_radius=15, width=160
                )
            )

        # Display Top Files
        top_files = get_top_large_files(self.all_files)
        self.top_files_list.controls.clear()
        for f in top_files:
            self.top_files_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.FILE_PRESENT, color="cyan", size=20),
                        ft.Text(f['name'], expand=True, size=13),
                        ft.Text(f"{round(f['size']/1e6, 2)} MB", color="cyan")
                    ]),
                    bgcolor="#16191F", padding=12, border_radius=10
                )
            )

        self.dashboard.visible = True
        self.progress_bar.visible = False
        self.log(f"Scan complete. {len(self.all_files)} files indexed.")
        self.page.update()

    def start_dupe(self, e):
        if not self.all_files: return
        self.stop_event.clear()
        self.stop_btn.visible = True
        self.stop_btn.disabled = False
        threading.Thread(target=self.run_dupe, daemon=True).start()

    def run_dupe(self):
        self.progress_bar.visible = True
        self.log("Hashing candidates...")
        # Passing stop_event to the backend logic
        self.detected_dupes = find_duplicates(
            self.all_files, progress_callback=self.update_prog, stop_event=self.stop_event
        )
        
        if self.stop_event.is_set():
            self.log("PROCESS ABORTED by user.")
        else:
            self.log(f"Finished. {len(self.detected_dupes)} duplicates found.")
            for o, d in self.detected_dupes:
                self.log(f"DUPE FOUND: {os.path.basename(d)}")

        self.progress_bar.visible = False
        self.stop_btn.visible = False
        self.progress_text.value = ""
        self.page.update()

    def show_org_menu(self, e):
        if not self.target_path: return
        dlg = ft.AlertDialog(
            title=ft.Text("NEXUS ORGANIZER"),
            content=ft.Text("Execute migration or Dry Run?"),
            actions=[
                ft.TextButton("DRY RUN", on_click=lambda _: self.run_org(True, dlg)),
                ft.ElevatedButton("EXECUTE", on_click=lambda _: self.run_org(False, dlg), bgcolor="cyan", color="black"),
            ]
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def run_org(self, is_dry, dlg):
        dlg.open = False
        self.page.update()
        if is_dry:
            self.log("--- DRY RUN START ---")
            plan = get_organize_plan(self.target_path)
            for name, dest in plan:
                self.log(f"PLAN: {name} -> [{dest}]")
            self.log("--- DRY RUN END ---")
        else:
            self.log("Starting File Migration...")
            count = organize_folder(self.target_path, dry_run=False)
            self.log(f"Migration Complete. {count} files sorted.")
            self.run_scan() # Refresh dashboard

    def clean_dupes(self, e):
        if not self.detected_dupes:
            self.log("Nothing to delete.")
            return
        self.log(f"Purging {len(self.detected_dupes)} files...")
        count = delete_files([p[1] for p in self.detected_dupes])
        self.log(f"Success. {count} files removed.")
        self.detected_dupes = []
        self.run_scan()

def main(page: ft.Page):
    NexusApp(page)

if __name__ == "__main__":
    ft.app(target=main)