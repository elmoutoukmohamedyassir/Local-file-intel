import pathlib
from datetime import datetime

def get_all_files(target_directory):
    """Scans a directory and returns a list of file metadata dictionaries."""
    file_data = []
    path = pathlib.Path(target_directory)

    # rglob('*') finds every file in every subfolder
    for file in path.rglob('*'):
        if file.is_file():
            try:
                stats = file.stat()
                file_data.append({
                    'name': file.name,
                    'path': str(file.absolute()),
                    'size': stats.st_size, # Bytes
                    'ext': file.suffix.lower(),
                    'modified': datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d')
                })
            except (PermissionError, OSError):
                continue # Skip files we can't access
    
    return file_data