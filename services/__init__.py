"""Service modules for File Orchestration System."""

from .duplicate_finder import find_duplicates, check_plagiarism, is_text_file
from .undo_manager import record_action, undo_last_batch
from .virus_scan import scan_folder

__all__ = [
    'find_duplicates',
    'check_plagiarism',
    'is_text_file',
    'record_action',
    'undo_last_batch',
    'scan_folder'
]

