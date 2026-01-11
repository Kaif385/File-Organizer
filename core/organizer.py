import shutil
import os
from pathlib import Path

def organize_files(folder_path, selected_files=None):
    folder = Path(folder_path)
    if not folder.is_dir():
        return {"status": "error", "message": "Invalid directory"}

    EXT_GROUPS = {
        "Images": [".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg", ".tiff"],
        "Videos": [".mp4", ".mkv", ".mov", ".avi", ".flv", ".wmv", ".webm"],
        "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt",
                      ".xls", ".xlsx", ".ppt", ".pptx", ".csv"],
        "Audio": [".mp3", ".wav", ".aac", ".flac", ".ogg", ".wma"],
        "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".iso"],
        "Code": [".py", ".js", ".html", ".css", ".java", ".cpp",
                 ".c", ".php", ".json", ".xml", ".sql"],
        "Executables": [".exe", ".msi", ".bat", ".sh", ".apk", ".app"]
    }

    count = 0
    recorded_moves = []

    files_to_process = [Path(f) for f in selected_files] if selected_files else []

    for f in files_to_process:
        if not f.exists():
            continue

        ext = f.suffix.lower()
        category = "Others"
        for cat, exts in EXT_GROUPS.items():
            if ext in exts:
                category = cat
                break

        target_dir = folder / category
        target_dir.mkdir(parents=True, exist_ok=True)

        target_path = target_dir / f.name

        if target_path.exists() and not f.samefile(target_path):
            stem = f.stem
            suffix = f.suffix
            counter = 1
            while target_path.exists():
                target_path = target_dir / f"{stem}_{counter}{suffix}"
                counter += 1

        try:
            if f.resolve() != target_path.resolve():
                shutil.move(str(f), str(target_path))

                recorded_moves.append({
                    "src": str(f),
                    "dest": str(target_path),
                    "type": "organize"
                })

                count += 1

        except Exception as e:
            return {"status": "error", "message": f"Failed to move {f.name}: {str(e)}", "organized_files": count, "moves": recorded_moves}

    return {
        "status": "success",
        "organized_files": count,
        "moves": recorded_moves
    }