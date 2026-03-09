from scanner import get_all_files
from analyzer import get_top_large_files

def run_app():
    target = input("Enter the folder path to scan (e.g., C:/Users/Name/Downloads): ")
    
    print(f"\n--- Scanning {target} ---")
    all_files = get_all_files(target)
    print(f"Found {len(all_files)} files.")

    # Show Large Files
    print("\n--- Top 5 Largest Files ---")
    top_files = get_top_large_files(all_files, count=5)
    for i, f in enumerate(top_files, 1):
        size_mb = round(f['size'] / (1024 * 1024), 2)
        print(f"{i}. {f['name']} ({size_mb} MB)")

if __name__ == "__main__":
    run_app()