# File Organizer

A Python application for file management, duplicate detection, and organization.

## Features

- **Folder Analysis** - View file statistics and distribution
- **Auto Organization** - Categorize and organize files by type (Images, Documents, Audio, Videos, Code, Archives, Executables)
- **Duplicate Detection** - Find duplicate files using MD5 hashing or content similarity analysis
- **Backup & Recovery** - Create and restore backups with optional ZIP compression
- **Undo System** - Reverse any file operations using transaction-based history
- **Security Scanning** - Detect and quarantine suspicious files

## Installation

```bash
pip install -r requirements.txt
python launcher.py
```

The app will open in your browser at `http://localhost:8501`

## Usage

1. Select a folder in the sidebar
2. Choose an action:
   - **Folder Analysis** - View file statistics and distribution (file counts, total size, file types, largest files, empty folders)
   - **Organize Files** - Auto-categorize files by type with batch operations
   - **Find Duplicates** - Find exact duplicates (MD5 hashing) or similar content (TF-IDF + cosine similarity)
   - **Backup** - Create folder backups with optional ZIP compression
   - **Security** - Scan for suspicious files and quarantine them
   - **Undo Actions** - Reverse any operations (all changes logged in JSON history)

## Technical Details

### Architecture
- **UI Framework**: Streamlit
- **Data Processing**: Pandas
- **ML/Analytics**: scikit-learn (TF-IDF vectorization)
- **Hashing**: MD5, SHA-256
- **File Operations**: Python pathlib, shutil

### Key Algorithms
- **Exact Duplicates**: MD5 binary hashing with size grouping
- **Content Similarity**: TF-IDF vectorization + cosine similarity (configurable threshold 0-100%)
- **File Organization**: Extension-based categorization into 7 categories
- **Undo System**: Transaction-based JSON history with batch operation reversal

### Project Structure

```
core/
  analyzer.py         - Folder analysis and statistics
  organizer.py        - File categorization logic
  backup.py           - Backup creation and restoration
  file_helpers.py     - File utility functions

services/
  duplicate_finder.py - Duplicate detection and plagiarism checking
  undo_manager.py     - Transaction history and reversal
  virus_scan.py       - Security scanning and quarantine
```

## Key Features Explained

### Duplicate Detection
- **Mode 1 (Exact Match)**: Compares file hashes for binary-identical duplicates
- **Mode 2 (Content Similarity)**: Uses TF-IDF vectorization to find similar documents regardless of formatting

### Undo System
- All file operations are recorded as transactions in JSON
- Batch operations can be reversed in reverse order
- Full audit trail of all changes
- Automatic recovery from corrupted state

### File Organization
Automatically categorizes into:
- Images (.jpg, .png, .gif, .bmp, etc.)
- Documents (.pdf, .docx, .txt, .xlsx, etc.)
- Videos (.mp4, .mkv, .avi, .mov, etc.)
- Audio (.mp3, .wav, .flac, .aac, etc.)
- Code (.py, .js, .java, .cpp, etc.)
- Archives (.zip, .rar, .7z, etc.)
- Executables (.exe, .msi, .sh, etc.)

## Error Handling
- Permission errors handled gracefully with partial completion
- Corrupted JSON recovery with fallback state
- Large file processing with streaming
- Path validation to prevent directory traversal

## Configuration

Edit `config.py` to customize:
- Default backup folder location
- File categories and extensions
- Virus scan settings
- Undo history retention

## License

MIT
