from scanner import get_all_files
from analyzer import get_top_large_files, find_duplicates, get_storage_by_extension, delete_files
from organizer import organize_folder, get_organize_plan

def run_app():
    print("=== Local File Intelligence System ===")
    target = input("Enter folder path: ").strip()
    
    all_files = get_all_files(target)
    if not all_files: 
        print("No files found. Check the path and try again.")
        return

    detected_dupes = []

    while True:
        print("\n" + "="*30)
        print("MAIN MENU")
        print("="*30)
        print("1. View Storage Report")
        print("2. Find Duplicate Files")
        print("3. Organize Folder (Sort by Type)")
        print("4. DELETE Detected Duplicates ⚠️")
        print("5. Exit")
        
        choice = input("\nSelect an option (1-5): ")

        if choice == '1':
            print("\n--- STORAGE REPORT ---")
            ext_data = get_storage_by_extension(all_files)
            for ext, size in sorted(ext_data.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"{ext.upper():<10}: {round(size/(1024*1024), 2)} MB")
            
            print("\n--- TOP 5 LARGEST FILES ---")
            top = get_top_large_files(all_files, count=5)
            for i, f in enumerate(top, 1):
                print(f"{i}. {f['name']} ({round(f['size']/(1024*1024), 2)} MB)")
        
        elif choice == '2':
            detected_dupes = find_duplicates(all_files)
            print(f"Found {len(detected_dupes)} duplicate pairs.")
            if detected_dupes and input("Show paths? (y/n): ").lower() == 'y':
                for o, d in detected_dupes: 
                    print(f"\n[ORIGINAL]:  {o}\n[DUPLICATE]: {d}")

        elif choice == '3':
            confirm = input("Run a Dry Run first? (y/n): ")
            is_dry = True if confirm.lower() == 'y' else False
            
            if is_dry:
                print("\n--- DRY RUN PLAN ---")
                plan = get_organize_plan(target)
                if not plan:
                    print("No loose files found in the root directory to organize.")
                else:
                    for file_name, dest_folder in plan:
                        print(f"Will move: {file_name} -> {dest_folder}/")
                print("\nDry run complete. No files were actually moved.")
            else:
                moved = organize_folder(target, dry_run=False)
                print(f"\nSuccess! Moved {moved} files.")
                
                # Refresh state so our index isn't stale
                print("Refreshing file index...")
                all_files = get_all_files(target)

        elif choice == '4':
            if not detected_dupes:
                print(" No duplicates detected yet. Run Option 2 first!")
            else:
                print(f" WARNING: You are about to delete {len(detected_dupes)} files.")
                confirm = input(f"Are you absolutely sure? Type 'DELETE' to confirm: ")
                if confirm == "DELETE":
                    paths_to_remove = [pair[1] for pair in detected_dupes]
                    count = delete_files(paths_to_remove)
                    print(f" Successfully removed {count} files.")
                    
                    detected_dupes = []
                    # Refresh state so our index isn't stale
                    print("Refreshing file index...")
                    all_files = get_all_files(target)
                else:
                    print("Deletion cancelled.")

        elif choice == '5':
            print("Goodbye!")
            break

if __name__ == "__main__":
    run_app()