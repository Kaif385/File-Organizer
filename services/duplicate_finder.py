import os
import hashlib
import difflib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

IGNORED_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.mp4', '.mp3', '.wav',
    '.exe', '.dll', '.bin', '.sys', '.msi', '.pyc',
    '.zip', '.rar', '.7z', '.tar', '.gz'
}

def is_text_file(filepath):
    
    ext = os.path.splitext(filepath)[1].lower()
    if ext in IGNORED_EXTENSIONS:
        return False
    
    try:
        with open(filepath, 'rb') as f:
            chunk = f.read(1024)
            if b'\0' in chunk: 
                return False
    except:
        return False
    return True

def read_text_file(filepath):
    encodings = ['utf-8', 'cp1252', 'latin-1', 'ascii']
    for enc in encodings:
        try:
            with open(filepath, 'r', encoding=enc) as f:
                return f.read() 
        except:
            continue
    return None

def check_plagiarism(file_list, threshold=50):
    
    documents = []
    valid_files = []

    for path in file_list:
        content = read_text_file(path)
        if content and len(content.strip()) > 0:
            documents.append(content)
            valid_files.append(path)

    if len(documents) < 2:
        return []

    vectorizer = TfidfVectorizer().fit_transform(documents)
    vectors = vectorizer.toarray()
    
    results = []
    n = len(valid_files)


    custom_css = """
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 10px; background-color: #ffffff; }
        table.diff { 
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace; 
            font-size: 12px;
            width: 100%; 
            border-collapse: collapse; 
            border: 1px solid #ddd;
            table-layout: fixed; /* Fixes the width overflow */
        }
        .diff_header { 
            background-color: #f7f7f7; 
            color: #999; 
            text-align: right; 
            width: 40px; 
            padding-right: 5px; 
            border-right: 1px solid #ddd;
            user-select: none;
        }
        .diff_next { background-color: #c0c0c0; }
        .diff_add { background-color: #e6ffec; color: #24292e; }
        .diff_chg { background-color: #fff5b1; color: #24292e; }
        .diff_sub { background-color: #ffebe9; color: #24292e; text-decoration: none; }
        
        /* The important part: showing code exactly as written */
        .diff_content { 
            white-space: pre-wrap; /* Wraps long lines so they don't cut off */
            word-break: break-all;
            padding-left: 10px;
            color: #24292e;
        }
        
        /* Container styling */
        .legend { display: none; } /* Hide the ugly default legend */
    </style>
    """

    for i in range(n):
        for j in range(i + 1, n):
            score = cosine_similarity([vectors[i]], [vectors[j]])[0][0]
            percentage = round(score * 100, 2)

            if percentage >= threshold:
                lines_a = documents[i].splitlines()
                lines_b = documents[j].splitlines()
                
                diff_table = difflib.HtmlDiff(tabsize=4, wrapcolumn=None).make_table(
                    lines_a, 
                    lines_b, 
                    context=True,  
                    numlines=5
                )
                
                full_html = f"{custom_css}<div>{diff_table}</div>"

                results.append({
                    "file_a": valid_files[i],
                    "file_b": valid_files[j],
                    "score": percentage,
                    "diff_html": full_html
                })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results

def find_duplicates(folder_path):
    """Find exact duplicate files using MD5 hash comparison."""
    from collections import defaultdict
    size_map = defaultdict(list)
    
    try:
        for root, _, files in os.walk(folder_path):
            for f in files:
                full = os.path.join(root, f)
                try:
                    size_map[os.path.getsize(full)].append(full)
                except (OSError, PermissionError):
                    pass
        
        duplicates = []
        for paths in size_map.values():
            if len(paths) < 2:
                continue
                
            hash_map = defaultdict(list)
            for p in paths:
                try:
                    with open(p, 'rb') as file:
                        h = hashlib.md5(file.read()).hexdigest()
                        hash_map[h].append(p)
                except (OSError, PermissionError):
                    pass
            
            for group in hash_map.values():
                if len(group) > 1:
                    duplicates.append(group)
        
        return duplicates
    except Exception as e:
        print(f"Error finding duplicates: {e}")
        return []