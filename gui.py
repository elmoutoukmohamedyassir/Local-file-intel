import flet as ft
import os
from scanner import get_all_files
from analyzer import find_duplicates, delete_files, get_top_large_files, get_storage_by_extension
from organizer import organize_folder

def main(page: ft.Page):
    page.title = "Local File Intelligence Pro"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 900
    page.window.height = 950
    page.scroll = "auto"

    # State
    scanned_data = []
    dupes_found = []

    # --- UI COMPONENTS ---
    path_input = ft.TextField(
        label="Target Path", 
        value="C:/Users/Name/Downloads", # Change this to your test folder!
        expand=True
    )
    
    status_msg = ft.Text("System Ready", color="blue")
    progress_ring = ft.ProgressRing(width=16, height=16, visible=False)
    dry_run_switch = ft.Switch(label="Dry Run (Safe Mode)", value=True)
    
    storage_report = ft.Column()
    top_files_report = ft.Column()
    dupe_report = ft.Column()

    def update_ui(scanning=False):
        progress_ring.visible = scanning
        path_input.disabled = scanning
        page.update()

    def run_full_analysis(e):
        nonlocal scanned_data
        if not path_input.value: return
        status_msg.value = " Scanning..."
        update_ui(True)
        
        scanned_data = get_all_files(path_input.value)
        
        # Update Storage Report
        ext_data = get_storage_by_extension(scanned_data)
        storage_report.controls.clear()
        storage_report.controls.append(ft.Text("Storage by Type", weight="bold"))
        for ext, size in sorted(ext_data.items(), key=lambda x: x[1], reverse=True)[:5]:
            storage_report.controls.append(ft.Text(f"{ext.upper()}: {round(size/(1024*1024), 2)} MB"))

        # Update Top Files
        top_files = get_top_large_files(scanned_data, count=5)
        top_files_report.controls.clear()
        top_files_report.controls.append(ft.Text("Top 5 Largest", weight="bold"))
        for f in top_files:
            top_files_report.controls.append(ft.Text(f"{f['name']} ({round(f['size']/(1024*1024), 2)} MB)", size=12))

        status_msg.value = " Analysis Complete!"
        update_ui(False)

    def find_dupes_ui(e):
        nonlocal dupes_found
        status_msg.value = " Hashing files..."
        update_ui(True)
        dupes_found = find_duplicates(scanned_data)
        dupe_report.controls.clear()
        dupe_report.controls.append(ft.Text(f"Found {len(dupes_found)} duplicates", weight="bold"))
        status_msg.value = " Duplicates identified."
        update_ui(False)

    def delete_dupes_ui(e):
        if not dupes_found: return
        count = delete_files([pair[1] for pair in dupes_found])
        status_msg.value = f" Deleted {count} files!"
        page.update()

    def run_organizer_ui(e):
        if not path_input.value: return
        status_msg.value = " Organizing..."
        page.update()
        
        # Calls the logic from your organizer.py
        moved = organize_folder(path_input.value, dry_run=dry_run_switch.value)
        
        mode = "DRY RUN" if dry_run_switch.value else "EXECUTED"
        status_msg.value = f" {mode}: Processed {moved} files."
        page.update()

    # --- LAYOUT ---
    page.add(
        ft.Text("File Intelligence Pro", size=32, weight="bold", color="blue"),
        ft.Row([path_input, ft.ElevatedButton("Scan & Analyze", icon="SEARCH", on_click=run_full_analysis)]),
        ft.Row([status_msg, progress_ring]),
        ft.Divider(),
        
        # Stats Dashboard
        ft.Row([
            ft.Container(storage_report, padding=15, bgcolor="surfaceVariant", border_radius=10, expand=1),
            ft.Container(top_files_report, padding=15, bgcolor="surfaceVariant", border_radius=10, expand=1),
        ]),
        
        ft.Divider(),
        
        # Tools Section
        ft.Text("Action Tools", size=20, weight="bold"),
        ft.Row([
            ft.ElevatedButton("Find Duplicates", icon="COPY", on_click=find_dupes_ui),
            ft.FilledButton("Delete Duplicates", icon="DELETE", bgcolor="red", on_click=delete_dupes_ui),
        ]),
        
        ft.Divider(),
        
        # Organizer Section
        ft.Container(
            content=ft.Column([
                ft.Text("Auto-Organizer", size=20, weight="bold"),
                ft.Text("Sorts files into Images, Docs, Video folders based on extension."),
                ft.Row([dry_run_switch, ft.ElevatedButton("Organize Folder", icon="AUTO_AWESOME", on_click=run_organizer_ui)]),
            ]),
            padding=15, bgcolor="#222222", border_radius=10
        ),
        
        dupe_report
    )

if __name__ == "__main__":
    ft.app(target=main)