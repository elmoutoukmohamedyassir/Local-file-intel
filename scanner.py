import pathlib
from datetime import datetime

def get_all_files(target_directory):
    file_data = []
    path = pathlib.Path(target_directory)
    
    # We use rglob but add error handling for system folders
    for file in path.rglob('*'):
        if 'venv' in file.parts or '.git' in file.parts or '.idea' in file.parts:
            continue

        if file.is_file():
            try:
                stats = file.stat()
                file_data.append({
                    'name': file.name,
                    'path': str(file.absolute()),
                    'size': stats.st_size,  
                    'ext': file.suffix.lower(),
                    'modified': datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d')
                })
            except (PermissionError, OSError):
                continue 
    return file_data