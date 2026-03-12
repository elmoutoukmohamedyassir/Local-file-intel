import pathlib
import shutil
import os

EXTENSION_MAP = {
    'Images': ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.bmp'],
    'Documents': ['.pdf', '.docx', '.txt', '.xlsx', '.pptx', '.csv'],
    'Videos': ['.mp4', '.mkv', '.mov', '.avi'],
    'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
    'Audio': ['.mp3', '.wav', '.flac', '.m4a'],
    'Setup': ['.exe', '.msi']
}

def get_organize_plan(target_directory):
    path = pathlib.Path(target_directory)
    plan = []
    if not path.exists(): return []
    
    for file in path.iterdir():
        if file.is_file() and not file.name.endswith('.py'):
            ext = file.suffix.lower()
            dest = "Others"
            for category, extensions in EXTENSION_MAP.items():
                if ext in extensions:
                    dest = category
                    break
            plan.append((file.name, dest))
    return plan

def organize_folder(target_directory, dry_run=True):
    path = pathlib.Path(target_directory)
    moved_count = 0
    if dry_run: return 0
    
    for file in path.iterdir():
        if file.is_file() and not file.name.endswith('.py'):
            ext = file.suffix.lower()
            dest_folder = "Others"
            for category, extensions in EXTENSION_MAP.items():
                if ext in extensions:
                    dest_folder = category
                    break
            
            dest_dir = path / dest_folder
            dest_dir.mkdir(exist_ok=True)
            
            try:
                # Use string paths for shutil.move to avoid Windows issues
                shutil.move(str(file), str(dest_dir / file.name))
                moved_count += 1
            except:
                continue
    return moved_count