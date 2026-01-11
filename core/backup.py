import os
import shutil
import tempfile
import zipfile
import time

def backup_files(file_paths, compress=False):
    """
    Creates a backup of specified files.
    
    Args:
        file_paths: List of file paths to backup
        compress: Whether to create a ZIP archive
        
    Returns:
        List of backup file paths created, or None if no files
    """
    if not file_paths:
        return None
    
    try:
        backup_dir = os.path.join(tempfile.gettempdir(), "sfo_backups")
        os.makedirs(backup_dir, exist_ok=True)
        created = []
        timestamp = int(time.time())

        for src in file_paths:
            if not os.path.exists(src):
                continue
                
            try:
                dest_name = f"bkp_{timestamp}_{os.path.basename(src)}"
                dest = os.path.join(backup_dir, dest_name)
                shutil.copy2(src, dest)
                created.append(dest)
            except (PermissionError, OSError) as e:
                print(f"Warning: Could not backup {src}: {e}")
                pass

        if compress and created:
            try:
                zip_path = os.path.join(backup_dir, f"backup_{timestamp}.zip")
                with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                    for p in created:
                        zf.write(p, arcname=os.path.basename(p))
                return [zip_path]
            except Exception as e:
                print(f"Error creating ZIP archive: {e}")
                return created
                
        return created
        
    except Exception as e:
        print(f"Error during backup: {e}")
        return None
