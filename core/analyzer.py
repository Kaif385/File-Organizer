import os
from collections import Counter
import heapq

def analyze_files(folder_path, top_n=10):
    """
    Analyzes a folder and returns statistics about files.
    
    Args:
        folder_path: Path to the folder to analyze
        top_n: Number of largest files to return
        
    Returns:
        Tuple: (total_files, total_size_mb, files_by_type, top_largest, empty_folders)
    """
    
    folder_path = os.path.normpath(folder_path)
    print(f"--- 🔍 Starting Analysis on: {folder_path} ---") 

    total_files = 0
    total_size = 0
    files_by_type = Counter()
    largest_heap = [] 
    empty_folders = []

    try:
        for root, dirs, files in os.walk(folder_path):
            
            if not dirs and not files:
                empty_folders.append(root)

            for f in files:
                try:
                    full_path = os.path.join(root, f)
                    
                    if not os.path.exists(full_path):
                        continue
                    
                    size = os.path.getsize(full_path)
                    total_files += 1
                    total_size += size
                    
                    ext = os.path.splitext(f)[1].lower() or "no_ext"
                    files_by_type[ext] += 1
                    
                    if len(largest_heap) < top_n:
                        heapq.heappush(largest_heap, (size, full_path))
                    else:
                        heapq.heappushpop(largest_heap, (size, full_path))
                except (PermissionError, OSError) as e:
                    print(f"Warning: Could not access {full_path}: {e}")
                    continue

        top_largest = sorted(largest_heap, key=lambda x: x[0], reverse=True)
        top_largest = [(p, round(s / 1048576, 2)) for s, p in top_largest]
        
        total_size_mb = round(total_size / 1048576, 2)
        return total_files, total_size_mb, dict(files_by_type), top_largest, empty_folders
        
    except Exception as e:
        print(f"Error during folder analysis: {e}")
        return 0, 0, {}, [], []
