from scanner import get_all_files
from analyzer import get_top_large_files, find_duplicates, get_storage_by_extension

def run_app():
    print("=== Local File Intelligence System ===")
    target = input("Enter folder path to scan: ").strip()
    
    all_files = get_all_files(target)
    if not all_files:
        print("No files found.")
        return

    # 1. Storage by Type
    print("\n" + "="*30)
    print("STORAGE BY FILE TYPE")
    print("="*30)
    ext_data = get_storage_by_extension(all_files)
    # Sort by size (most used space first)
    sorted_ext = sorted(ext_data.items(), key=lambda x: x[1], reverse=True)
    for ext, size in sorted_ext[:10]: # Top 10 types
        size_mb = round(size / (1024 * 1024), 2)
        if size_mb > 0:
            print(f"{ext.upper():<10}: {size_mb} MB")

    # 2. Large Files
    print("\n" + "="*30)
    print("TOP 5 LARGEST FILES")
    print("="*30)
    top_files = get_top_large_files(all_files, count=5)
    for i, f in enumerate(top_files, 1):
        size_mb = round(f['size'] / (1024 * 1024), 2)
        print(f"{i}. {f['name']} | {size_mb} MB")

    # 3. Duplicates
    print("\n" + "="*30)
    print("SCANNING FOR DUPLICATES")
    print("="*30)
    dupes = find_duplicates(all_files)
    
    if dupes:
        print(f"Found {len(dupes)} duplicate pairs.")
        show_all = input("Show all duplicate paths? (y/n): ")
        if show_all.lower() == 'y':
            for original, duplicate in dupes:
                print(f"\n[!] Duplicate found:\n    O: {original}\n    D: {duplicate}")
    else:
        print("No duplicates found.")

    print("\n" + "="*30)
    print("Analysis Complete!")

if __name__ == "__main__":
    run_app()