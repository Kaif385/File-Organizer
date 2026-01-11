# File Organizer - Complete Functionality List

## Overview
File Organizer is a comprehensive file management system with 6 main features accessible through a sidebar navigation menu.

---

## 1. SELECT FOLDER (Initial Setup)
**Purpose:** Choose the working directory for all operations

### Capabilities:
- Browse and select any folder from the system
- Display current working path with breadcrumb navigation
- Validate folder existence before proceeding
- Prevent operations if no valid folder is selected
- Show "Change Folder" button to switch directories mid-session

**UI Elements:**
- File browser dialog (tkinter integration)
- Path display with breadcrumb
- Folder change button

---

## 2. FOLDER ANALYSIS
**Purpose:** Scan and analyze folder structure with deep insights

### Core Analysis Features:

#### File Statistics
- **Total Files Count** - All files in the folder and subfolders
- **Total Size** - Complete folder size in MB
- **File Type Distribution** - Breakdown by extension (.pdf, .jpg, etc.)
- **Top 10 Largest Files** - Identify storage hogs with file names and sizes
- **Empty Folders** - Detection and counting of empty subdirectories

#### File Tree View
- **Hierarchical Display** - Show complete folder structure with indentation
- **File Information Tooltips** - Display:
  - File size
  - File extension type
  - Last modified date
- **Quick Open** - "↗️" button to open any file in system default app
- **500-file Limit** - Tree view truncates for performance with large folders

#### File Integrity Checking (SHA-256 Hashing)
- **Run Integrity Check** - Calculate SHA-256 checksums for all files
- **Track Modified Files** - Compare current checksums against cached hashes
- **Modification Detection** - Flag any files that have changed since last check
- **Persistence** - Store checksums in `.integrity.json` for future comparisons
- **Visual Indicators:**
  - 🔥 icon marks modified files
  - ⚠️ warning shows count of modified files
- **Progress Bar** - Real-time progress during hash calculation

#### Timeline Analysis
- **File Age Distribution** - Categorize files by modification date:
  - **Today** - Modified in last 24 hours
  - **Week** - Modified in last 7 days
  - **Month** - Modified in last 30 days
  - **Older** - Files older than 30 days
- **Bar Chart Visualization** - Visual representation of file age distribution

#### Metrics Display
- **Metric Cards** - Visual KPIs showing:
  - Total Files count
  - Total Size in MB
  - Empty Folders count
- **File Type Chart** - Bar chart of file extensions

---

## 3. ORGANIZE FILES
**Purpose:** Auto-categorize and batch move files by type

### File Selection
- **File Tree Checkboxes** - Multi-select files with visual checkboxes
- **Select All Button** - Select all files in one click
- **Clear Selection Button** - Deselect all files at once
- **File Preview** - Show:
  - File name with icon (📄)
  - File extension
  - File size
  - Quick open button (↗️)
- **Selection Counter** - Display "Selected: X files"

### Auto-Categorization
Files organized into 7 categories based on extension:

1. **Images** - .jpg, .jpeg, .png, .gif, .bmp, .svg, .webp, .ico
2. **Documents** - .pdf, .docx, .doc, .xlsx, .xls, .pptx, .ppt, .txt, .rtf
3. **Videos** - .mp4, .mkv, .avi, .mov, .flv, .wmv, .webm, .m4v
4. **Audio** - .mp3, .wav, .flac, .aac, .wma, .ogg, .m4a
5. **Code** - .py, .js, .java, .cpp, .c, .go, .rs, .ts, .jsx, .tsx, .cs, .vb
6. **Archives** - .zip, .rar, .7z, .tar, .gz, .bz2, .iso
7. **Executables** - .exe, .msi, .app, .dmg, .sh, .bat, .cmd

### Batch Operations
- **Move Selected Files** - Move all checked files to category folders
- **Conflict Handling** - Auto-rename files if destination names exist
- **Transaction Recording** - Log all moves to undo.json
- **Status Feedback** - Show count of successfully moved files
- **Auto-folder Creation** - Create category folders if they don't exist

### Feedback
- Toast notification with count: "Moved X files successfully!"
- Error messages for failed operations
- Auto-rerun UI after completion

---

## 4. BACKUP FILES
**Purpose:** Create safety backups of important files

### File Selection
- **File Tree Checkboxes** - Multi-select files for backup (identical to Organize)
- **Select All Backup** - Select all files for backup
- **Clear Backup** - Clear all backup selections
- **Selection Counter** - Show "Selected: X files"
- **File Preview** - Display name, extension, size

### Backup Options
- **Compression Toggle** - Checkbox to create ZIP archive
  - Without ZIP: Files copied to `Backup` folder
  - With ZIP: Files compressed into single `.zip` file in `Backup` folder
- **Timestamp Naming** - Backups include creation timestamp

### Backup Features
- **Destination Folder** - Default: `Backup/` subdirectory
- **Recursive Backup** - Preserve folder structure inside backup
- **Auto-create Directory** - Create `Backup` folder if missing
- **Feedback** - Toast notification: "Backup created successfully!"

---

## 5. FIND DUPLICATES
**Purpose:** Detect duplicate files and similar content

### Mode 1: Exact Match (Hash Scan)
Uses MD5 hashing for binary-identical file detection

**Process:**
1. Scan all files in folder
2. Group by file size (optimization)
3. Calculate MD5 hash for each file
4. Identify files with identical hashes
5. Group and display results

**Features:**
- **Grouping** - Files displayed in groups of duplicates
- **Group Expanders** - Show/hide duplicate groups
- **File Count** - Display "Group 1 (3 files)" etc.
- **Quick Open** - Open each duplicate file directly
- **File Paths** - Show complete paths for clarity

**Limitations:**
- Only detects 100% identical files
- File names/locations can differ
- Detects copies of same file

### Mode 2: Content Similarity (TF-IDF Vectorization)
Finds similar files using machine learning algorithms

**Text File Support:**
- .txt, .py, .js, .java, .cpp, .md, .json, .xml, .csv, .html, .css, etc.
- Multi-encoding support: UTF-8, CP1252, Latin-1, ASCII
- Auto-detect text vs binary files

**Scanning Algorithm:**
1. Filter text files from folder (displays count found)
2. Use TF-IDF vectorization to analyze content
3. Calculate cosine similarity between all file pairs
4. Rank by similarity score

**User Controls:**
- **Select All Texts** - Quick button to select all compatible files
- **Clear All** - Deselect all files
- **File Browser** - Browse and preview text files (first 100 shown)
- **Multi-select** - Choose specific files to compare
- **Quick Access** - Open selected files directly
- **Threshold Slider** - Adjust matching sensitivity (0-100%)
  - 0% = very permissive (all files match)
  - 50% = balanced (good for plagiarism)
  - 100% = very strict (exact matches only)

**Results Display:**
- **Match Counter** - "Match 1 of 15"
- **Navigation** - Previous/Next buttons to browse matches
- **Similarity Score** - Large percentage display with color:
  - 🔴 Red (>80%) - Very high similarity
  - 🟠 Orange (50-80%) - Medium similarity
  - 🟢 Green (<50%) - Low similarity
- **File Names** - Display both compared files
- **Quick Actions** - "Open File A" and "Open File B" buttons

**Detailed Comparison:**
- **Diff HTML Viewer** - Side-by-side code comparison
- **Highlighted Differences** - Lines changed are marked
- **Line Numbers** - Show exact locations of changes
- **Color Coding:**
  - Green = additions
  - Red = deletions
  - Yellow = modifications
- **Scrollable View** - 600px height with scroll for large files

**Performance:**
- Can handle 50+ files (may take 5-10 seconds)
- Progress indicator during processing
- Error handling for import failures

---

## 6. VIRUS SCAN
**Purpose:** Detect and quarantine suspicious files

### Scanning Features
- **Live Scan Button** - Start security scan
- **Progress Bar** - Real-time progress (current/total files)
- **Status Text** - Show currently scanning file name
- **Completion Notification** - "Scan Complete!" message

### Suspicious File Detection
Identifies files by:
- **Executable Extensions** - .exe, .bat, .cmd, .msi, .com, .scr, .vbs, .js (when executable)
- **Script Files** - .ps1, .sh, .cmd (if marked executable)
- **Double Extensions** - .txt.exe, .pdf.exe (suspicious combinations)
- **Archive Bombs** - .zip files with suspicious ratios
- **Known Patterns** - Detection of known malware signatures

### Results Display
- **Total Files Scanned** - Show count
- **Infected Count** - Number of suspicious files found
- **List of Threats** - Each suspicious file shows:
  - 🔴 Red indicator
  - File path/name
  - Reason for detection (e.g., "Executable file")

### Quarantine System
- **Move All Button** - "☣️ Move All (X) to Quarantine Isolation"
- **Automatic Quarantine** - Files moved to `quarantine/` folder
- **Undo Support** - Quarantine moves are logged to undo history
- **Verification** - Before moving:
  - Check file exists
  - Create quarantine folder if needed
  - Handle path errors
- **Feedback** - Toast: "Files quarantined!"

### Safety Features
- Files isolated in separate directory
- No permanent deletion
- Complete audit trail
- Reversible via Undo Actions

---

## 7. UNDO ACTIONS
**Purpose:** Reverse file operations safely

### History Display
- **Total Batches Counter** - "📋 Total Batches: X"
- **Empty State** - "📭 No actions to undo" message
- **Batch List** - Shows all operations in reverse chronological order

### Batch Information
Each batch displays:
- **Batch Number** - "Batch 1, Batch 2, etc."
- **Action Type** - "Move", "Organize", "Quarantine"
- **File Count** - "Move (5 files)"
- **Expandable Details** - Click to show individual files

### File Details (in expander)
- **File Names** - Original file names
- **Source Paths** - Where files came from
- **Destination Paths** - Where files were moved
- **Preview** - First 10 files shown, count for rest
- **Message** - "... and X more files"

### Undo Operations
- **Undo Button** - "↩️ Undo Batch X" per batch
- **Individual Undo** - Reverse only specific batches
- **Sequential** - Process moves in reverse order to avoid conflicts
- **Validation** - Check paths exist before undoing
- **Error Handling** - Clear error messages if undo fails

### Process
1. Select batch to undo
2. Click "Undo Batch X" button
3. Show spinner: "Undoing batch X..."
4. Reverse all moves in that batch:
   - Move files back to original locations
   - Create intermediate folders if needed
   - Validate paths and permissions
5. Success: "✅ Undo successful!"
6. Auto-rerun UI to refresh display

### State Recovery
- **Corrupted JSON** - Auto-reset with warning: "⚠️ Undo log was corrupted. It has been reset."
- **Missing File** - Handle gracefully if original location deleted
- **Permission Errors** - Display: "❌ Undo failed. Check file permissions and paths."
- **Missing Log** - Show: "📭 No undo history file found"

---

## GLOBAL FEATURES

### Navigation
- **Sidebar Menu** - Quick access to all 6 features
- **Back/Forward Buttons** - Navigate between recently visited pages
- **Breadcrumb Path** - Show current working folder
- **Change Folder** - Switch directories anytime

### Session State Management
- **Persistent Selections** - Remember selected files during session
- **Session Variables** - Store:
  - Current folder path
  - Selected files for each operation
  - Analysis results
  - Scan results
  - Undo history
  - Match indices

### File Operations
- **Open in System App** - ↗️ button opens file with default handler
- **File Size Formatting** - Display sizes in KB, MB, GB
- **Path Display** - Show relative and absolute paths
- **Error Handling** - Graceful failures with user messages

### Performance Optimizations
- **Lazy Loading** - Modules imported only when needed
- **Tree Truncation** - Limit display to 500 items
- **Batch Processing** - Process files in chunks
- **Progress Indicators** - Spinners and progress bars for long operations

### Data Persistence
- **undo.json** - Transaction history
- **.integrity.json** - File checksum cache
- **Backup/ folder** - Backup storage
- **quarantine/ folder** - Isolated suspicious files

### Error Recovery
- **JSON Corruption** - Auto-reset with warning
- **Permission Errors** - Fallback and partial completion
- **Missing Modules** - Clear error messages with solutions
- **Invalid Paths** - Path validation before operations

---

## TECHNICAL SPECIFICATIONS

### Dependencies
- **Streamlit** - Web UI framework
- **Pandas** - Data processing
- **scikit-learn** - TF-IDF vectorization and similarity
- **Python pathlib** - File path handling
- **Python shutil** - File operations
- **Python hashlib** - MD5/SHA-256 hashing
- **Python json** - Data persistence
- **Python tkinter** - File browser dialog

### Data Storage
- **undo.json** - List of operation batches
- **.integrity.json** - File hash cache
- **Backup/** - User-created backups
- **quarantine/** - Isolated suspicious files

### Supported File Types (Text Analysis)
- Code: .py, .js, .java, .cpp, .ts, .jsx, .tsx, .cs, .vb, .go, .rs, .sql, .sh, .rb
- Documents: .txt, .md, .json, .xml, .html, .css, .yaml, .ini, .conf, .log
- Data: .csv, .tsv

### Limitations
- Text files max size: Practical limit ~50MB (TF-IDF vectorization)
- Folder analysis: Best performance with <100,000 files
- Integrity check: Slower with 10,000+ files (SHA-256 calculation)
- UI updates: Max 500 items displayed in tree view
- Quarantine: Limited only by storage space
