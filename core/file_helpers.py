import os
import streamlit as st
import hashlib

def _hash_key(p):
    return "f_" + hashlib.sha1(p.encode("utf-8")).hexdigest()

def select_files_in_folder(folder, include_subfolders=True):
    added = 0
    if not folder or not os.path.exists(folder):
        return 0
    
    if "selected_files" not in st.session_state: st.session_state["selected_files"] = []
    if "file_key_map" not in st.session_state: st.session_state["file_key_map"] = {}

    targets = []
    if include_subfolders:
        for r, _, files in os.walk(folder):
            for f in files:
                targets.append(os.path.join(r, f))
    else:
        try:
            for f in os.listdir(folder):
                p = os.path.join(folder, f)
                if os.path.isfile(p):
                    targets.append(p)
        except Exception:
            pass

    for p in targets:
        k = _hash_key(p)
        st.session_state["file_key_map"][k] = p
        
        if not st.session_state.get(k, False):
            st.session_state[k] = True
            st.session_state["selected_files"].append(p)
            added += 1
            
    return added