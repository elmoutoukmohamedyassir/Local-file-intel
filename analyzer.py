import hashlib
from scanner import get_all_files

def get_top_large_files(files, count=10):
    sorted_list = sorted(files, key=lambda x: x['size'], reverse=True)
    return sorted_list[:count]

def get_storage_by_extension(files):
    summary = {}
    for f in files:
        ext = f['ext'] if f['ext'] else "No Extension"
        summary[ext] = summary.get(ext, 0) + f['size']
    return summary

def calculate_hash(filepath):
    """Calculates the SHA-256 hash in chunks to save memory."""
    hasher = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()
    except:
        return None

def find_duplicates(files):
    """Finds duplicates efficiently by only hashing files with matching sizes."""
    size_map = {}
    duplicates = []

    
    for f in files:
        size = f['size']
        if size > 0: 
            size_map.setdefault(size, []).append(f)

   
    candidates = {size: paths for size, paths in size_map.items() if len(paths) > 1}
    
    total_candidates = sum(len(paths) for paths in candidates.values())
    print(f"Found {total_candidates} potential duplicates to verify...")

    
    processed_count = 0
    for size, potential_dupes in candidates.items():
        hashes = {}
        for f in potential_dupes:
            processed_count += 1
            print(f"Hashing candidate {processed_count}/{total_candidates}...", end='\r')
            
            file_hash = calculate_hash(f['path'])
            if file_hash:
                if file_hash in hashes:
                    duplicates.append((hashes[file_hash], f['path']))
                else:
                    hashes[file_hash] = f['path']
    
    print(f"\nVerification complete.")
    return duplicates