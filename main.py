from scanner import get_all_files
from analyzer import get_top_large_files, find_duplicates, get_storage_by_extension
from organizer import organize_folder

def run_app():
    print("=== Local File Intelligence System ===")
    target = input("Enter folder path: ").strip()
    
    all_files = get_all_files(target)
    if not all_files: return

    
    ext_data = get_storage_by_extension(all_files)
    top_files = get_top_large_files(all_files, count=5)
    
    
    print(f"\nScan Complete. {len(all_files)} files found.")

    
    while True:
        print("\nWhat would you like to do?")
        print("1. View Storage Report (Top Types & Large Files)")
        print("2. Find Duplicate Files")
        print("3. Organize this Folder (Sort by Extension)")
        print("4. Exit")
        
        choice = input("\nSelect an option (1-4): ")

        if choice == '1':
            print("\nTOP TYPES:")
            for ext, size in sorted(ext_data.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"{ext.upper()}: {round(size/(1024*1024), 2)} MB")
        
        elif choice == '2':
            dupes = find_duplicates(all_files)
            print(f"Found {len(dupes)} duplicates.")
            if dupes and input("Show paths? (y/n): ").lower() == 'y':
                for o, d in dupes: print(f"D: {d}\nO: {o}\n")

        elif choice == '3':
            confirm = input("Run a Dry Run first? (y/n): ")
            is_dry = True if confirm.lower() == 'y' else False
            organize_folder(target, dry_run=is_dry)
            if not is_dry:
                print("Note: Run a new scan to update data after moving files.")

        elif choice == '4':
            break

if __name__ == "__main__":
    run_app()