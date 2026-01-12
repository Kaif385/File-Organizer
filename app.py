import os
import shutil
import tempfile
import json
import time
import hashlib
import importlib
import platform
import subprocess
import tkinter as tk
from tkinter import filedialog
import streamlit as st
import pandas as pd
from pathlib import Path
import datetime

st.set_page_config(
    page_title="Smart File Organizer Pro", 
    page_icon="📂", 
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UNDO_FILE = os.path.join(BASE_DIR, "undo.json")
QUARANTINE_DIR = os.path.join(BASE_DIR, "SFO_Quarantine") 
INTEGRITY_FILE = os.path.join(BASE_DIR, "integrity_cache.json")

st.markdown("""
<style>
    /* Global Font & Theme */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Button Styling */
    .stButton > button {
        width: 100%;
        border-radius: 6px;
        height: 38px;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
        border: 1px solid #d1d5db;
    }
    
    /* Primary Action Buttons */
    .stButton > button[kind="primary"] {
        background-color: #2563eb; 
        color: white;
        border: none;
    }
    
    /* Active Sidebar Item */
    section[data-testid="stSidebar"] .stRadio > label:has(input:checked) > div { 
        background-color: #eff6ff; 
        color: #1d4ed8 !important; 
        border-radius: 4px;
        font-weight: 600;
        border-left: 3px solid #1d4ed8;
    }
    
    /* --- UPDATED: CLASSIC SELECT FOLDER BOX --- */
    
    /* The Container */
    .select-folder-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 20px;          /* Compact padding */
        background-color: #fff; /* Clean white background */
        border-radius: 8px; 
        border: 1px solid #d1d5db; /* Classic solid border */
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        margin: 10px auto;
        max-width: 80%;         /* Keeps it from getting too wide */
    }

    /* The Icon (Folder Emoji) */
    .select-folder-icon {
        font-size: 40px;        /* Reduced from default large size */
        margin-bottom: 8px;
        line-height: 1;
    }

    /* The Title ("No Folder Selected") */
    .select-folder-title {
        font-size: 18px;        /* Classic header size */
        font-weight: 600;
        color: #374151;         /* Dark gray */
        margin-bottom: 4px;
    }

    /* The Description Text */
    .select-folder-desc {
        font-size: 13px;        /* Smaller description text */
        color: #6b7280;         /* Lighter gray */
        margin: 0;
    }

</style>
""", unsafe_allow_html=True)

def open_system_file(filepath):
    """Opens file using the System Default Application."""
    clean_path = os.path.normpath(filepath)
    if not os.path.exists(clean_path):
        st.toast(f"File not found: {clean_path}", icon="❌")
        return
    try:
        if platform.system() == 'Windows':
            os.startfile(clean_path)
        elif platform.system() == 'Darwin':
            subprocess.call(('open', clean_path))
        else:
            subprocess.call(('xdg-open', clean_path))
    except Exception as e:
        st.error(f"Error: {e}")

def format_size(n):
    for unit in ["B", "KB", "MB", "GB"]:
        if n < 1024: return f"{n:.2f} {unit}"
        n /= 1024
    return f"{n:.2f} TB"

def get_hash(p):
    return hashlib.md5(p.encode('utf-8')).hexdigest()

def get_file_sha256(filepath):
    """Calculates SHA-256 hash for integrity checks."""
    hasher = hashlib.sha256()
    try:
        with open(filepath, 'rb') as file:
            while chunk := file.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()
    except:
        return None

def ensure_dirs():
    if not os.path.exists(QUARANTINE_DIR):
        os.makedirs(QUARANTINE_DIR, exist_ok=True)

def lazy_import(module_name, func_name):
    try:
        mod = importlib.import_module(module_name)
        return getattr(mod, func_name)
    except ImportError as e:
        st.error(f"❌ Error loading {module_name}: {e}")
        return None

def open_folder_dialog():
    """Hybrid Folder Picker."""
    folder_path = None
    try:
        root = tk.Tk()
        root.withdraw()
        root.wm_attributes('-topmost', 1)
        folder_path = filedialog.askdirectory(master=root, title="Select Folder")
        root.destroy()
        return folder_path
    except:
        pass

    if platform.system() == 'Windows':
        try:
            cmd = """
            powershell -Command "Add-Type -AssemblyName System.Windows.Forms; $d = New-Object System.Windows.Forms.FolderBrowserDialog; $d.Description = 'Select a Folder'; if ($d.ShowDialog() -eq 'OK') { $d.SelectedPath }"
            """
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            path = result.stdout.strip()
            if path: return path
        except: pass
    return None

def get_file_tree(path):
    """Generates a list of files and folders for tree view."""
    if os.path.normpath(path) == os.path.normpath(QUARANTINE_DIR):
        st.error("Access Denied: Cannot browse the Quarantine directory.")
        return []
        
    items = []
    try:
        for root, dirs, files in os.walk(path):
            rel_path = os.path.relpath(root, path)
            level = 0 if rel_path == "." else rel_path.count(os.sep) + 1
            if rel_path != ".":
                items.append({"type": "folder", "path": root, "name": os.path.basename(root), "level": level})
            for f in files:
                full_path = os.path.join(root, f)
                items.append({"type": "file", 
                    "path": full_path, 
                    "name": f, 
                    "level": level + 1, 
                    "size": os.path.getsize(full_path),
                    "modified": os.path.getmtime(full_path),
                    "type_ext": os.path.splitext(f)[1]
                })
    except: pass
    return items

if "folder_path" not in st.session_state: st.session_state["folder_path"] = ""
if "selected_files" not in st.session_state: st.session_state["selected_files"] = []
if "backup_selected_files" not in st.session_state: st.session_state["backup_selected_files"] = []
if "duplicates_to_delete" not in st.session_state: st.session_state["duplicates_to_delete"] = []
if "integrity_cache" not in st.session_state: st.session_state["integrity_cache"] = {}

if "nav_history" not in st.session_state: st.session_state["nav_history"] = ["Select Folder"]
if "nav_index" not in st.session_state: st.session_state["nav_index"] = 0

def on_sidebar_change():
    new_page = st.session_state["nav_radio_selection"]
    current_page = st.session_state["nav_history"][st.session_state["nav_index"]]
    if new_page != current_page:
        st.session_state["nav_history"] = st.session_state["nav_history"][:st.session_state["nav_index"]+1]
        st.session_state["nav_history"].append(new_page)
        st.session_state["nav_index"] += 1

def go_back():
    if st.session_state["nav_index"] > 0:
        st.session_state["nav_index"] -= 1
        prev_page = st.session_state["nav_history"][st.session_state["nav_index"]]
        st.session_state["nav_radio_selection"] = prev_page

def go_forward():
    if st.session_state["nav_index"] < len(st.session_state["nav_history"]) - 1:
        st.session_state["nav_index"] += 1
        next_page = st.session_state["nav_history"][st.session_state["nav_index"]]
        st.session_state["nav_radio_selection"] = next_page

top_c1, top_c2, top_c3 = st.columns([8, 0.7, 0.7])
with top_c1: st.title("📂 File Manager Pro")
can_go_back = st.session_state["nav_index"] > 0
with top_c2: st.button("⬅", on_click=go_back, disabled=not can_go_back, help="Go Back", use_container_width=True)
can_go_fwd = st.session_state["nav_index"] < len(st.session_state["nav_history"]) - 1
with top_c3: st.button("➡", on_click=go_forward, disabled=not can_go_fwd, help="Go Forward", use_container_width=True)

current_page_from_history = st.session_state["nav_history"][st.session_state["nav_index"]]

with st.sidebar:
    st.header("Menu")
    page = st.radio(
        "Navigate:", 
        ["Select Folder", "Folder Analysis", "Organize Files", "Backup Files", "Find Duplicates", "Virus Scan", "Undo Actions"],
        index=["Select Folder", "Folder Analysis", "Organize Files", "Backup Files", "Find Duplicates", "Virus Scan", "Undo Actions"].index(current_page_from_history),
        key="nav_radio_selection",
        on_change=on_sidebar_change
    )
    st.markdown("---")
    fpath = st.session_state["folder_path"]
    if fpath and os.path.exists(fpath):
        st.success(f"Active: **{os.path.basename(fpath)}**")
    else:
        st.info("No folder selected")

if page != "Select Folder" and (not fpath or not os.path.exists(fpath)):
    st.warning("Please go to 'Select Folder' tab and choose a valid directory first.")
    st.stop()
    
if fpath and os.path.exists(fpath):
    if os.path.normpath(fpath) == os.path.normpath(QUARANTINE_DIR):
        st.error(f"🔴 WARNING: Quarantine Isolation Directory!")
    path_parts = Path(fpath).parts
    breadcrumb_html = " / ".join([f"<span style='color: #2563eb; font-weight: 500;'>{p}</span>" for p in path_parts])
    st.markdown(f"""
    <div style='margin-bottom: 20px; padding: 10px; background-color: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0;'>
        📍 <b>Location:</b> {breadcrumb_html}
    </div>
    """, unsafe_allow_html=True)


if page == "Select Folder":
    st.header("📥 Select Working Directory")
    
    if st.session_state["folder_path"]:
        st.markdown("""
        <div style="text-align: center; padding: 30px; background-color: #f0fdf4; border: 2px solid #bbf7d0; border-radius: 10px; margin-bottom: 15px;">
            <h2 style="color: #166534; margin:0;">✅ Ready to Organize</h2>
            <p style="color: #15803d; margin-top: 8px; font-size: 1.1em;">
                Current Active Folder:
            </p>
            <code style="background: white; padding: 5px 10px; border-radius: 4px; font-size: 1.1em;">{}</code>
        </div>
        """.format(st.session_state["folder_path"]), unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([3, 2, 3])
        with c2:
            if st.button("📂 Change Folder", type="secondary", use_container_width=True):
                selected = open_folder_dialog() 
                if selected:
                    st.session_state["folder_path"] = os.path.normpath(selected)
                    st.session_state["selected_files"] = [] 
                    st.rerun()
    else:
        st.markdown("""
        <div class="select-folder-container">
            <div class="select-folder-icon">📂</div>
            <div class="select-folder-title">No Folder Selected</div>
            <div class="select-folder-desc">Please select a folder from your computer to start organizing, analyzing, and cleaning your files.</div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns([3, 2, 3])
        with c2:
            if st.button("📂 Browse Folder to Start", type="primary", use_container_width=True):
                selected = open_folder_dialog()
                if selected:
                    st.session_state["folder_path"] = os.path.normpath(selected)
                    st.session_state["selected_files"] = [] 
                    st.rerun()

elif page == "Folder Analysis":
    st.header("📊 Folder Analysis")
    
    if st.checkbox("📂 Show File Tree", key="ana_tree"):
        items = get_file_tree(fpath)
        st.markdown("### Folder Structure")
        integrity_check = st.button("🔄 Run File Integrity Check (SHA-256)")
        
        cached_integrity = {}
        if os.path.exists(INTEGRITY_FILE):
            with open(INTEGRITY_FILE, 'r') as f:
                try: cached_integrity = json.load(f)
                except: pass

        new_hashes = {}
        modified_files = []
        
        if integrity_check:
            with st.spinner("Calculating checksums for all files..."):
                prog_bar = st.progress(0)
                total_items = len([i for i in items if i["type"]=="file"])
                processed = 0
                for item in items:
                    if item["type"] == "file":
                        rel_path = os.path.relpath(item["path"], fpath)
                        current_hash = get_file_sha256(item["path"])
                        new_hashes[rel_path] = current_hash
                        if rel_path in cached_integrity and cached_integrity[rel_path] != current_hash:
                            modified_files.append(rel_path)
                        processed += 1
                        prog_bar.progress(min(1.0, processed/max(1, total_items)))
            
            with open(INTEGRITY_FILE, 'w') as f: json.dump(new_hashes, f, indent=4)
            st.session_state["modified_files_list"] = modified_files
            st.toast("Integrity check complete!", icon="✅")
            st.rerun()

        if "modified_files_list" in st.session_state and st.session_state["modified_files_list"]:
            st.warning(f"🚨 {len(st.session_state['modified_files_list'])} modified files detected!")
            for mf in st.session_state['modified_files_list']: st.markdown(f"**- ⚠️ {mf}**")
            st.markdown("---")

        for item in items[:500]:
            indent = "&nbsp;" * (item["level"] * 4)
            if item["type"] == "folder":
                st.markdown(f"{indent}📁 **{item['name']}**", unsafe_allow_html=True)
            else:
                rel_path = os.path.relpath(item['path'], fpath)
                is_modified = rel_path in st.session_state.get("modified_files_list", [])
                tooltip = f"Size: {format_size(item['size'])} | Type: {item['type_ext']} | Modified: {datetime.datetime.fromtimestamp(item['modified']).strftime('%Y-%m-%d')}"
                c1, c2 = st.columns([0.85, 0.15]) 
                with c1:
                    icon = "🔥" if is_modified else "📄"
                    st.markdown(f"{indent}{icon} {item['name']} <span style='color:#aaa; font-size:0.8em'>({item['type_ext']})</span>", unsafe_allow_html=True)
                    st.caption(tooltip)
                with c2:
                    if st.button("↗️", key=f"ana_open_{get_hash(item['path'])}"): open_system_file(item['path'])
        if len(items) > 500: st.caption("...tree truncated.")
        st.markdown("---")

    if st.button("Run Analysis", type="primary"):
        analyze = lazy_import("core.analyzer", "analyze_files")
        if analyze:
            with st.spinner(" analyzing file metrics..."):
                st.session_state["analysis_res"] = analyze(fpath)
                now = time.time()
                trends = {"Today": 0, "Week": 0, "Month": 0, "Older": 0}
                all_files = get_file_tree(fpath)
                for i in all_files:
                    if i["type"]=="file":
                        age = now - i["modified"]
                        if age < 86400: trends["Today"]+=1
                        elif age < 604800: trends["Week"]+=1
                        elif age < 2592000: trends["Month"]+=1
                        else: trends["Older"]+=1
                st.session_state["trends"] = trends
                st.toast("Analysis updated", icon="📊")
                st.rerun()
    
    if "analysis_res" in st.session_state:
        res = st.session_state["analysis_res"]
        
        if "trends" in st.session_state:
            st.subheader("📅 File Age Distribution")
            st.bar_chart(st.session_state["trends"])
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"<div class='metric-card'><div class='metric-value'>{res[0]}</div><div class='metric-label'>Total Files</div></div>", unsafe_allow_html=True)

            c2.markdown(f"<div class='metric-card'><div class='metric-value'>{res[1]} MB</div><div class='metric-label'>Total Size</div></div>", unsafe_allow_html=True)

            c3.markdown(f"<div class='metric-card'><div class='metric-value'>{len(res[4])}</div><div class='metric-label'>Empty Folders</div></div>", unsafe_allow_html=True)
            
        st.subheader("📂 File Types")
        if res[2]: st.bar_chart(res[2])
        
        st.subheader("💎 Top Largest Files")
        for path, size in res[3]:
            c1, c2, c3 = st.columns([0.7, 0.1, 0.2])
            c1.text(os.path.basename(path))
            if c2.button("↗️", key=f"ana_l_{get_hash(path)}"): open_system_file(path)
            c3.text(f"{size} MB")

elif page == "Organize Files":
    st.header("🧹 Organize Files")
    
    show_tree = st.checkbox("📂 Show File Tree", key="org_tree_toggle")
    if show_tree:
        items = get_file_tree(fpath)
        if not items: st.info("Folder is empty.")
        else:
            c1, c2 = st.columns(2)
            if c1.button("Select All"):
                st.session_state["selected_files"] = [i["path"] for i in items if i["type"] == "file"]
                st.rerun()
            if c2.button("Clear Selection"):
                st.session_state["selected_files"] = []
                st.rerun()
            
            st.markdown("---")
            for item in items:
                indent = "&nbsp;" * (item["level"] * 4)
                if item["type"] == "folder":
                    st.markdown(f"{indent}📁 **{item['name']}**", unsafe_allow_html=True)
                    continue
                uid = get_hash(item["path"])
                chk_key = f"chk_{uid}"
                if chk_key not in st.session_state: st.session_state[chk_key] = item["path"] in st.session_state["selected_files"]
                c_chk, c_open, c_size = st.columns([0.7, 0.1, 0.2])
                with c_chk:
                    st.checkbox(f"{indent}📄 {item['name']}", key=chk_key)
                    if st.session_state[chk_key]:
                        if item["path"] not in st.session_state["selected_files"]: st.session_state["selected_files"].append(item["path"])
                    else:
                        if item["path"] in st.session_state["selected_files"]: st.session_state["selected_files"].remove(item["path"])
                with c_open:
                    if st.button("↗️", key=f"open_{uid}"): open_system_file(item["path"])
                with c_size: st.caption(format_size(item["size"]))

    st.markdown("---")
    st.info(f"Selected: {len(st.session_state['selected_files'])} files")
    
    if st.button("🚀 Move Selected Files", type="primary"):
        organize = lazy_import("core.organizer", "organize_files")
        undo_manager = lazy_import("services.undo_manager", "record_action")
        if not st.session_state["selected_files"]:
            st.toast("No files selected!", icon="⚠️")
        elif organize:
            with st.spinner("Organizing files..."):
                res = organize(fpath, st.session_state["selected_files"])
                if res.get("status") == "success":
                    moves = res.get("moves", [])
                    if moves and undo_manager:
                        undo_manager(moves)
                    st.toast(f"Moved {res['organized_files']} files successfully!", icon="✅")
                    st.session_state["selected_files"] = []
                    time.sleep(1.5)
                    st.rerun()
                else:
                    st.error(res.get("message"))
        else:
            st.error("❌ Failed to load required modules")

elif page == "Backup Files":
    st.header("💾 Backup Files")
    show_tree_bkp = st.checkbox("📂 Show File Tree", key="bkp_tree_toggle")
    if show_tree_bkp:
        items = get_file_tree(fpath)
        if items:
            c1, c2 = st.columns(2)
            if c1.button("Select All Backup"):
                st.session_state["backup_selected_files"] = [i["path"] for i in items if i["type"] == "file"]
                st.rerun()
            if c2.button("Clear Backup"):
                st.session_state["backup_selected_files"] = []
                st.rerun()
            st.markdown("---")
            for item in items:
                indent = "&nbsp;" * (item["level"] * 4)
                if item["type"] == "folder":
                    st.markdown(f"{indent}📁 **{item['name']}**", unsafe_allow_html=True)
                    continue
                uid = get_hash(item["path"] + "_bkp")
                chk_key = f"chk_bkp_{uid}"
                if chk_key not in st.session_state: st.session_state[chk_key] = item["path"] in st.session_state["backup_selected_files"]
                c_chk, c_open, c_size = st.columns([0.7, 0.1, 0.2])
                with c_chk:
                    st.checkbox(f"{indent}📄 {item['name']}", key=chk_key)
                    if st.session_state[chk_key]:
                        if item["path"] not in st.session_state["backup_selected_files"]: st.session_state["backup_selected_files"].append(item["path"])
                    else:
                        if item["path"] in st.session_state["backup_selected_files"]: st.session_state["backup_selected_files"].remove(item["path"])
                with c_open:
                    if st.button("↗️", key=f"op_bkp_{uid}"): open_system_file(item["path"])
                with c_size: st.caption(format_size(item["size"]))

    st.markdown("---")
    st.info(f"Selected: {len(st.session_state['backup_selected_files'])} files")
    compress = st.checkbox("Compress as ZIP")
    
    if st.button("Create Backup", type="primary"):
        backup = lazy_import("core.backup", "backup_files")
        if not st.session_state["backup_selected_files"]:
            st.toast("No files selected!", icon="⚠️")
        elif backup:
            with st.spinner("Creating backup archive..."):
                backup(st.session_state["backup_selected_files"], compress)
                st.toast("Backup created successfully!", icon="✅")
                st.session_state["backup_selected_files"] = []
                time.sleep(1)
                st.rerun()

elif page == "Find Duplicates":
    st.header("🕵️ Duplicate & Content Finder")
    
    if st.checkbox("📂 Show File Tree", key="dup_tree"):
        items = get_file_tree(fpath)
        st.markdown("### Folder Structure")
        for item in items[:300]:
            indent = "&nbsp;" * (item["level"] * 4)
            if item["type"] == "folder": st.markdown(f"{indent}📁 **{item['name']}**", unsafe_allow_html=True)
            else:
                c1, c2 = st.columns([0.85, 0.15]) 
                with c1: st.markdown(f"{indent}📄 {item['name']}", unsafe_allow_html=True)
                with c2: 
                    if st.button("↗️", key=f"dup_open_{get_hash(item['path'])}"): open_system_file(item['path'])
        st.markdown("---")

    mode = st.radio("Select Scan Mode:", ["⚡ Exact Match (Hash Scan)", "📊 Content Similarity Check"], horizontal=True)

    if mode == "⚡ Exact Match (Hash Scan)":
        if st.button("Scan for Exact Duplicates"):
            finder = lazy_import("services.duplicate_finder", "find_duplicates")
            if finder:
                with st.spinner("Scanning for binary duplicates..."):
                    st.session_state["dups"] = finder(fpath)
                    st.session_state["plagiarism_results"] = None
        
        if "dups" in st.session_state and st.session_state["dups"]:
            dups = st.session_state["dups"]
            st.success(f"Found {len(dups)} groups of exact duplicates.")
            for i, group in enumerate(dups):
                with st.expander(f"Group {i+1} ({len(group)} files)"):
                    for f in group:
                        c1, c2 = st.columns([0.8, 0.2])
                        c1.text(f)
                        if c2.button("Open", key=f"op_dup_{get_hash(f)}"): open_system_file(f)

    else:
        st.info("📊 Similarity Mode: Analyzes content to find similar files.")
        compatible_files = []
        is_safe = lazy_import("services.duplicate_finder", "is_text_file")
        if is_safe:
            for root, _, files in os.walk(fpath):
                for f in files:
                    full_p = os.path.join(root, f)
                    if is_safe(full_p): compatible_files.append(full_p)
        
        with st.expander(f"📂 Browse & Preview Compatible Files ({len(compatible_files)} found)"):
            if not compatible_files: st.write("No text files found.")
            else:
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("✅ Select All Texts", key="select_all_texts", use_container_width=True):
                        st.session_state["selected_for_scan_temp"] = compatible_files
                        st.rerun()
                with c2:
                    if st.button("❌ Clear All", key="clear_all_texts", use_container_width=True):
                        st.session_state["selected_for_scan_temp"] = []
                        st.rerun()
                st.markdown("---")
                for p in compatible_files[:100]: 
                    c1, c2 = st.columns([0.85, 0.15])
                    rel_name = os.path.relpath(p, fpath)
                    c1.text(rel_name)
                    if c2.button("↗️", key=f"browse_{abs(hash(p))}"): open_system_file(p)

        selected_for_scan = st.multiselect("Select files to compare:", options=compatible_files, format_func=lambda x: os.path.relpath(x, fpath), default=st.session_state.get("selected_for_scan_temp", []))
        
        if selected_for_scan:
            st.caption("Quick Access:")
            cols = st.columns(len(selected_for_scan) if len(selected_for_scan) < 4 else 4)
            for i, p in enumerate(selected_for_scan):
                with cols[i % 4]:
                    if st.button(f"↗️ {os.path.basename(p)}", key=f"sel_open_{i}"): open_system_file(p)
            st.markdown("---")

        threshold = st.slider("Similarity Threshold (%)", 0, 100, 50)
        
        if st.button("🚀 Scan Files", type="primary"):
            if len(selected_for_scan) < 2:
                st.toast("Select at least 2 files.", icon="⚠️")
            else:
                checker = lazy_import("services.duplicate_finder", "check_plagiarism")
                if checker:
                    with st.spinner("⏳ Comparing files... (This may take a moment)"):
                        try:
                            results = checker(selected_for_scan, threshold)
                            st.session_state["plagiarism_results"] = results
                            if not results:
                                st.toast("No matches found.", icon="✅")
                                st.success("✅ Scan Complete: No similar files found.")
                        except ImportError:
                            st.error("❌ Critical: Install scikit-learn!")
                        except Exception as e:
                            st.error(f"Error: {e}")

        if "plagiarism_results" in st.session_state and st.session_state["plagiarism_results"]:
            results = st.session_state["plagiarism_results"]
            if "match_index" not in st.session_state: st.session_state["match_index"] = 0
            total_matches = len(results)
            if st.session_state["match_index"] >= total_matches: st.session_state["match_index"] = 0

            if total_matches == 0:
                st.success("No matches found.")
            else:
                st.markdown("---")
                nav_col1, nav_col2, nav_col3 = st.columns([6, 1, 1])
                with nav_col1: st.subheader(f"🚨 Match {st.session_state['match_index'] + 1} of {total_matches}")
                with nav_col2:
                    if st.button("⬅ Prev", key="nav_prev", use_container_width=True):
                        if st.session_state["match_index"] > 0:
                            st.session_state["match_index"] -= 1
                            st.rerun()
                with nav_col3:
                    if st.button("Next ➡", key="nav_next", use_container_width=True):
                        if st.session_state["match_index"] < total_matches - 1:
                            st.session_state["match_index"] += 1
                            st.rerun()

                current_res = results[st.session_state["match_index"]]
                score = current_res['score']
                color = "#dc2626" if score > 80 else "#f59e0b" if score > 50 else "#16a34a"
                name_a = os.path.basename(current_res['file_a'])
                name_b = os.path.basename(current_res['file_b'])

                st.markdown(f"""
                    <div style="text-align: center; background-color: #ffffff; padding: 20px; border-radius: 12px; border-top: 6px solid {color}; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px;">
                        <h1 style="margin:0; color: {color}; font-size: 3.5em;">{score}%</h1>
                        <p style="margin:0; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">Similarity Detected</p>
                        <hr style="margin: 15px 0; border-color: #f1f5f9;">
                        <div style="display: flex; justify-content: space-around; align-items: center; font-size: 1.1em;">
                            <span>📄 <b>{name_a}</b></span>
                            <span style='color:#cbd5e1'>vs</span>
                            <span>📄 <b>{name_b}</b></span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                b1, b2, b3 = st.columns([1, 0.2, 1])
                with b1:
                    if st.button(f"📂 Open {name_a}", key=f"main_op_a_{st.session_state['match_index']}", use_container_width=True): open_system_file(current_res['file_a'])
                with b3:
                    if st.button(f"📂 Open {name_b}", key=f"main_op_b_{st.session_state['match_index']}", use_container_width=True): open_system_file(current_res['file_b'])

                # Highlight button - opens floating highlighted view when pressed
                c1, c2 = st.columns([1, 1])
                with c1:
                    if st.button(f"🔦 Highlight Matches", key=f"highlight_{st.session_state['match_index']}", use_container_width=True):
                        st.components.v1.html(current_res.get('highlight_html', current_res['diff_html']), height=800)

elif page == "Virus Scan":
    st.header("🛡️ Virus Scan")
    
    st.info("Scanning checks for suspicious file extensions and known bad patterns. (API integration ready)")
    
    if st.button("Run Live Scan", type="primary"):
        scanner = lazy_import("services.virus_scan", "scan_folder")
        if scanner:
            progress_bar = st.progress(0)
            status_text = st.empty()
            final_result = None
            
            for update in scanner(fpath):
                if update['type'] == 'progress':
                    current = update['scanned']
                    total = update['total']
                    perc = min(1.0, current / max(1, total))
                    progress_bar.progress(perc)
                    status_text.text(f"Scanning ({current}/{total}): {update['file']}")
                elif update['type'] == 'complete':
                    final_result = update
            
            progress_bar.empty()
            status_text.success("Scan Complete!")
            st.session_state["scan_res"] = final_result
            
    if "scan_res" in st.session_state:
        res = st.session_state["scan_res"]
        st.info(f"Total Scanned: {res['scanned']} files.")
        
        if res['infected']:
            st.error(f"Found {len(res['infected'])} suspicious files.")
            suspicious_files = [x['file'] for x in res['infected']]
            
            if st.button(f"☣️ Move All ({len(suspicious_files)}) to Quarantine Isolation", type="primary"):
                ensure_dirs()
                undo_manager = lazy_import("services.undo_manager", "record_action")
                moved_items = []
                for item in suspicious_files:
                    if not os.path.isabs(item): full_path = os.path.join(fpath, item)
                    else: full_path = item
                        
                    if not os.path.exists(full_path): continue 
                    dest = os.path.join(QUARANTINE_DIR, os.path.basename(item))
                    try:
                        shutil.move(full_path, dest)
                        moved_items.append({"type": "quarantine", "src": full_path, "dest": dest})
                    except Exception as e: st.error(f"Failed to move {item}: {e}")
                
                if moved_items and undo_manager: undo_manager(moved_items)
                st.toast("Files quarantined!", icon="☣️")
                st.rerun()
            
            for inf in res['infected']:
                st.write(f"🔴 **{inf['file']}**: {inf['reason']}")
        else:
            st.success("No suspicious files found.")

elif page == "Undo Actions":
    st.header("↩️ Undo History")
    undoer = lazy_import("services.undo_manager", "undo_last_batch")
    undo_last_action = lazy_import("services.undo_manager", "undo_last_action")
    
    # Quick Undo Button for Most Recent Action
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔙 Undo Last Action", use_container_width=True, type="primary"):
            if undo_last_action:
                with st.spinner("Reversing last action..."):
                    res = undo_last_action()
                    if isinstance(res, tuple):
                        success, message = res
                        if success:
                            st.toast(f"✅ {message}", icon="🔙")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                    else:
                        # Fallback for old behavior (boolean)
                        if res:
                            st.toast("✅ Last action reversed!", icon="🔙")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Undo failed. Check file permissions.")
            else:
                st.error("❌ Undo manager not available")
    
    st.markdown("---")
    
    if os.path.exists(UNDO_FILE):
        try:
            with open(UNDO_FILE) as f: 
                content = f.read()
                if not content.strip(): history = []
                else: history = json.loads(content)
            
            if not history:
                st.info("📭 No actions to undo. Your file operations will appear here.")
            else:
                st.markdown(f"**📋 Total Batches:** {len(history)}")
                st.markdown("---")
                
                for i, batch in enumerate(reversed(history)):
                    batch_id = len(history) - 1 - i
                    count = len(batch) if isinstance(batch, list) else 0
                    
                    if not batch or not isinstance(batch, list):
                        continue
                    
                    action_type = batch[0].get("type", "Move").capitalize()
                    
                    # Create an expander for each batch showing details
                    with st.expander(f"**Batch {batch_id + 1}:** {action_type} ({count} files)", expanded=False):
                        # Show file details
                        for item in batch[:10]:  # Show first 10 files
                            src = item.get("src", "Unknown")
                            dest = item.get("dest", "Unknown")
                            if src:
                                st.caption(f"📄 {os.path.basename(src)}")
                                st.caption(f"   → {os.path.relpath(dest, fpath) if dest else 'Unknown'}")
                        
                        if len(batch) > 10:
                            st.caption(f"... and {len(batch) - 10} more files")
                        
                        st.markdown("---")
                        col1, col2, col3 = st.columns([1, 1, 1])
                        
                        with col2:
                            if st.button(f"↩️ Undo Batch {batch_id + 1}", key=f"undo_{batch_id}", use_container_width=True, type="primary"):
                                if undoer:
                                    with st.spinner(f"Undoing batch {batch_id + 1}..."):
                                        res = undoer(batch_id)
                                        if res:
                                            st.toast("✅ Undo successful!", icon="↩️")
                                            time.sleep(1)
                                            st.rerun()
                                        else:
                                            st.error("❌ Undo failed. Check file permissions and paths.")
                                else:
                                    st.error("❌ Undo manager not available")
                
        except (json.JSONDecodeError, ValueError):
            st.warning("⚠️ Undo log was corrupted. It has been reset.")
            with open(UNDO_FILE, 'w') as f: json.dump([], f)
        except Exception as e:
            st.error(f"Error reading undo log: {e}")
    else:
        st.info("📭 No undo history file found. Your file operations will appear here.")