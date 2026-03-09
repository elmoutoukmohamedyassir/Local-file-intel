from scanner import get_all_files

def get_top_large_files(files, count=10):
    """Sorts files by size and returns the top ones."""
    # We use a 'lambda' to tell Python to sort by the 'size' key
    sorted_list = sorted(files, key=lambda x: x['size'], reverse=True)
    return sorted_list[:count]

def get_storage_by_extension(files):
    """Groups storage usage by file type (e.g., .jpg, .mp4)."""
    summary = {}
    for f in files:
        ext = f['ext'] if f['ext'] else "No Extension"
        summary[ext] = summary.get(ext, 0) + f['size']
    return summary