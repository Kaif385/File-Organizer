import os
import hashlib
import difflib
import html as _html
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
    except Exception:
        return False
    return True


def read_text_file(filepath):
    encodings = ['utf-8', 'cp1252', 'latin-1', 'ascii']
    for enc in encodings:
        try:
            with open(filepath, 'r', encoding=enc) as f:
                return f.read()
        except Exception:
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

    custom_css = '''<style>body{font-family:Segoe UI,sans-serif;margin:0;padding:10px}table.diff{font-family:Consolas,monospace;font-size:12px;width:100%;border-collapse:collapse;border:1px solid #ddd;table-layout:fixed}.diff_header{background-color:#f7f7f7;color:#999;text-align:right;width:40px;padding-right:5px}.diff_next{background-color:#c0c0c0}.diff_add{background-color:#e6ffec;color:#24292e}.diff_chg{background-color:#fff5b1;color:#24292e}.diff_sub{background-color:#ffebe9;color:#24292e}.diff_content{white-space:pre-wrap;word-break:break-all;padding-left:10px}.legend{display:none}</style>'''

    for i in range(n):
        for j in range(i + 1, n):
            score = cosine_similarity([vectors[i]], [vectors[j]])[0][0]
            percentage = round(score * 100, 2)

            if percentage >= threshold:
                lines_a = documents[i].splitlines()
                lines_b = documents[j].splitlines()

                diff_table = difflib.HtmlDiff(tabsize=4, wrapcolumn=None).make_table(lines_a, lines_b, context=True, numlines=5)
                full_html = f'<html><head>{custom_css}</head><body>{diff_table}</body></html>'

                try:
                    sm = difflib.SequenceMatcher(None, lines_a, lines_b)
                    match_a = [False] * len(lines_a)
                    match_b = [False] * len(lines_b)
                    for tag, a1, a2, b1, b2 in sm.get_opcodes():
                        if tag == 'equal':
                            for aa in range(a1, a2):
                                match_a[aa] = True
                            for bb in range(b1, b2):
                                match_b[bb] = True

                    def build_col(lines, marks, title):
                        rows = []
                        for idx, ln in enumerate(lines):
                            safe = _html.escape(ln)
                            cls = 'match' if marks[idx] else 'normal'
                            rows.append(f"<div class='{cls}'><span class='ln'>{idx+1:4d}</span> <span class='content'>{safe}</span></div>")
                        return f"<div class='col'><div class='col-title'>{_html.escape(title)}</div>" + "\n".join(rows) + "</div>"

                    col_a = build_col(lines_a, match_a, os.path.basename(valid_files[i]))
                    col_b = build_col(lines_b, match_b, os.path.basename(valid_files[j]))
                    highlight_body = f"<div class='hl-container'>{col_a}{col_b}</div>"
                    highlight_css = '''<style>.hl-container{display:flex;gap:12px;font-family:Consolas,monospace;background:#fff;padding:12px;border-radius:8px}.col{flex:1;max-width:50%;overflow:auto;border:1px solid #eee;padding:8px}.col-title{font-weight:600;padding-bottom:6px}.ln{color:#999;display:inline-block;width:48px}.content{white-space:pre-wrap;word-break:break-word}.match{background:#fffbcc}.normal{background:transparent}.modal-backdrop{position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.35);display:flex;align-items:center;justify-content:center}.modal{background:#fff;border-radius:10px;padding:16px;max-width:95%;max-height:90%;overflow:auto;box-shadow:0 10px 30px rgba(0,0,0,0.2)}.modal .close{position:sticky;float:right;margin-bottom:8px}</style>'''
                    highlight_html = f'<html><head>{custom_css}{highlight_css}</head><body><div class=\"modal-backdrop\"><div class=\"modal\"><button class=\"close\" onclick=\"document.querySelector(\".modal-backdrop\").style.display=\"none\"\">Close</button>{highlight_body}</div></div></body></html>'
                except Exception:
                    highlight_html = full_html

                results.append({"file_a": valid_files[i], "file_b": valid_files[j], "score": percentage, "diff_html": full_html, "highlight_html": highlight_html})

    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def find_duplicates(folder_path):
    duplicates = []
    hash_map = {}

    try:
        for root, _, files in os.walk(folder_path):
            for f in files:
                p = os.path.join(root, f)
                if not os.path.isfile(p):
                    continue
                ext = os.path.splitext(p)[1].lower()
                if ext in IGNORED_EXTENSIONS:
                    continue
                try:
                    with open(p, 'rb') as file:
                        h = hashlib.md5(file.read()).hexdigest()
                        hash_map.setdefault(h, []).append(p)
                except (OSError, PermissionError):
                    pass

        for group in hash_map.values():
            if len(group) > 1:
                duplicates.append(group)

        return duplicates
    except Exception as e:
        print(f"Error finding duplicates: {e}")
        return []
