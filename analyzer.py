import hashlib
import os

def calculate_hash(filepath, stop_event=None):
    hasher = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(65536):
                # CHECK FOR STOP SIGNAL INSIDE THE FILE READ LOOP
                if stop_event and stop_event.is_set():
                    return "STOPPED"
                hasher.update(chunk)
        return hasher.hexdigest()
    except:
        return None

def find_duplicates(files, progress_callback=None, stop_event=None):
    size_map = {}
    for f in files:
        size_map.setdefault(f['size'], []).append(f)

    candidates = [group for group in size_map.values() if len(group) > 1 and group[0]['size'] > 0]
    total = sum(len(g) for g in candidates)
    processed = 0
    duplicates = []

    for group in candidates:
        hashes = {}
        for f in group:
            if stop_event and stop_event.is_set(): return duplicates
            
            processed += 1
            if progress_callback: progress_callback(processed, total, f['name'])
            
            h = calculate_hash(f['path'], stop_event)
            if h == "STOPPED": return duplicates
            
            if h:
                if h in hashes:
                    duplicates.append((hashes[h], f['path']))
                else:
                    hashes[h] = f['path']
    return duplicates

def get_storage_by_extension(files):
    summary = {}
    for f in files:
        ext = f['ext'] if f['ext'] else "Unknown"
        summary[ext] = summary.get(ext, 0) + f['size']
    return summary

def get_top_large_files(files, count=5):
    return sorted(files, key=lambda x: x['size'], reverse=True)[:count]

def delete_files(file_paths):
    deleted = 0
    for p in file_paths:
        try:
            if os.path.exists(p):
                os.remove(p)
                deleted += 1
        except: continue
    return deleted