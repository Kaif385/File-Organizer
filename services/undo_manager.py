import os
import json
import shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UNDO_FILE = os.path.join(BASE_DIR, "undo.json")

def record_action(moves_list):
    """Record a batch of file operations for undo capability."""
    history = []
    if os.path.exists(UNDO_FILE):
        try:
            with open(UNDO_FILE, "r") as f:
                content = f.read().strip()
                if content:
                    history = json.loads(content)
        except (json.JSONDecodeError, ValueError):
            history = []
    
    history.append(moves_list)
    
    with open(UNDO_FILE, "w") as f:
        json.dump(history, f, indent=2)

def undo_last_batch(index):
    """Undo a specific batch of operations by reversing file moves."""
    if not os.path.exists(UNDO_FILE):
        return False
    
    try:
        with open(UNDO_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                return False
            history = json.loads(content)
    except (json.JSONDecodeError, ValueError):
        return False
    
    if index < 0 or index >= len(history):
        return False
    
    batch = history[index]
    
    if not batch or not isinstance(batch, list):
        return False
    
    # Process moves in REVERSE order to undo properly
    for action in reversed(batch):
        try:
            current_loc = action.get("dest")
            original_loc = action.get("src")
            
            # Validate paths exist and are strings
            if not current_loc or not original_loc:
                continue
            
            current_loc = os.path.normpath(current_loc)
            original_loc = os.path.normpath(original_loc)
            
            # Check if file is at destination (current location)
            if os.path.exists(current_loc):
                # Ensure source directory exists
                src_dir = os.path.dirname(original_loc)
                os.makedirs(src_dir, exist_ok=True)
                
                try:
                    shutil.move(current_loc, original_loc)
                except (PermissionError, OSError) as e:
                    print(f"Warning: Could not undo move of {current_loc}: {e}")
                    continue
            elif not os.path.exists(original_loc):
                # File is already at original location
                continue
                
        except Exception as e:
            print(f"Error processing undo action: {e}")
            continue
    
    # Remove the batch from history after successful undo
    del history[index]
    with open(UNDO_FILE, "w") as f:
        json.dump(history, f, indent=2)
    
    return True
