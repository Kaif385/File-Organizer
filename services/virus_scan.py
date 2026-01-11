import os

BAD_EXT = {'.exe', '.bat', '.cmd', '.vbs', '.ps1'}

def scan_folder(folder_path):
    
    scanned = 0
    infected = []
    
    total_files = sum([len(files) for r, d, files in os.walk(folder_path)])
    
    yield {"type": "start", "total": total_files}
    
    for root, _, files in os.walk(folder_path):
        for f in files:
            scanned += 1
            full_path = os.path.join(root, f)
            ext = os.path.splitext(f)[1].lower()
            
            yield {
                "type": "progress",
                "file": f,
                "scanned": scanned,
                "total": total_files
            }
            
            if ext in BAD_EXT:
                infected.append({"file": f, "reason": f"Suspicious extension {ext}"})
                
    yield {
        "type": "complete",
        "scanned": scanned,
        "infected": infected
    }