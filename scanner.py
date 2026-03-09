import pathlib
from datetime import datetime

def get_all_files(target_directory):
    """
    Scans a directory recursively and returns a list of dictionaries 
    containing metadata for every file found.
    """
    file_data = []
    path = pathlib.Path(target_directory)
    count = 0

    print(f"Starting scan in: {path.absolute()}")
    print("Searching for files (Press Ctrl+C to stop)...")

    # rglob('*') finds every file in every subfolder
    for file in path.rglob('*'):
        # PERFORMANCE TIP: Skip the 'venv' folder and hidden git folders
        if 'venv' in file.parts or '.git' in file.parts:
            continue

        if file.is_file():
            count += 1
            
            # Visual feedback every 100 files so you know it's working
            if count % 100 == 0:
                print(f"Items indexed: {count}...", end='\r')
            
            try:
                stats = file.stat()
                file_data.append({
                    'name': file.name,
                    'path': str(file.absolute()),
                    'size': stats.st_size,  # Size in Bytes
                    'ext': file.suffix.lower(),
                    'modified': datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d')
                })
            except (PermissionError, OSError):
                # This happens for system files or files currently in use
                continue 
    
    print(f"\n Scan complete! Total files found: {count}")
    return file_data

# This part only runs if you play scanner.py directly
if __name__ == "__main__":
    # Test with current directory
    data = get_all_files(".")
    for item in data[:5]:  # Show first 5 items as a sample
        print(item)