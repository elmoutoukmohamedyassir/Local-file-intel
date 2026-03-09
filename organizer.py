import pathlib
import shutil

# Define where extensions should go
EXTENSION_MAP = {
    'Images': ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.bmp'],
    'Documents': ['.pdf', '.docx', '.txt', '.xlsx', '.pptx', '.csv'],
    'Videos': ['.mp4', '.mkv', '.mov', '.avi'],
    'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
    'Audio': ['.mp3', '.wav', '.flac', '.m4a'],
    'Setup': ['.exe', '.msi']
}

def organize_folder(target_directory, dry_run=True):
    """Moves files into categorized folders based on their extensions."""
    path = pathlib.Path(target_directory)
    moved_count = 0

    print(f"\n--- {'DRY RUN' if dry_run else 'EXECUTING'} ORGANIZATION ---")

    # We only look at files in the TOP level of this folder 
    # (Organizing subfolders automatically can get messy!)
    for file in path.iterdir():
        if file.is_file():
            ext = file.suffix.lower()
            dest_folder_name = "Others" # Default

            # Find the right category
            for category, extensions in EXTENSION_MAP.items():
                if ext in extensions:
                    dest_folder_name = category
                    break
            
            # Create destination path
            dest_dir = path / dest_folder_name
            dest_path = dest_dir / file.name

            if dry_run:
                print(f"[WILL MOVE] {file.name} -> {dest_folder_name}/")
            else:
                # Actual moving logic
                dest_dir.mkdir(exist_ok=True) # Create folder if it doesn't exist
                try:
                    shutil.move(str(file), str(dest_path))
                    print(f"[MOVED] {file.name} -> {dest_folder_name}/")
                    moved_count += 1
                except Exception as e:
                    print(f"[ERROR] Could not move {file.name}: {e}")

    return moved_count