# PDF Stamping Tool

A Python utility for batch processing PDF documents by adding custom stamps with page count information.

## Features

- **Batch Processing**: Process multiple PDF files at once
- **Page Counting**: Automatically counts pages in each PDF (stored as variable N)
- **Custom Stamp Design**:
  - Round red box with rounded corners
  - "Received and Reviewed" text
  - Page count display
  - Two solid red lines
- **Automatic Output Management**: Creates organized output folder for stamped PDFs

## Installation

### ⚡ Quick Install (Windows - EASIEST)
Double-click **`INSTALL_NOW.bat`** and you're done!

### 📦 Manual Installation

1. **Prerequisites**: Make sure you have Python 3.7+ installed

2. **Install Dependencies**:

   **RECOMMENDED - Using python -m pip (works on all systems):**
   ```bash
   python -m pip install -r requirements.txt
   ```

   **Alternative - If you get "pip is not recognized" error:**
   ```bash
   python -m pip install PyPDF2==3.0.1 reportlab==4.0.7
   ```

   **Alternative - Using py launcher (some Windows systems):**
   ```bash
   py -m pip install -r requirements.txt
   ```

   **Why use `python -m pip` instead of just `pip`?**  
   On Windows, even when Python is installed, the `pip` command may not work directly. Using `python -m pip` always works because it runs pip through Python.

   **Troubleshooting**: If Python commands don't work, Python may not be installed. Download from [python.org](https://www.python.org/downloads/) and ensure "Add Python to PATH" is checked during installation.

## Usage

### Windows Quick Start (Easiest Method)

1. **Install dependencies** (one-time setup):
   - Double-click `install_windows.bat`
   - Wait for installation to complete

2. **Run the tool**:
   - Double-click `run_windows.bat` and follow the prompts
   - OR drag and drop a folder onto `run_windows.bat`
   - OR use command line: `run_windows.bat C:\path\to\pdfs`

### Basic Usage (All Platforms)

Process all PDFs in a folder:
```bash
python stamp_pdf.py <input_folder>
```

This will create a `stamped_pdfs` subfolder in the input directory with all processed files.

### Custom Output Folder

Specify a custom output location:
```bash
python stamp_pdf.py <input_folder> <output_folder>
```

### Examples

**Example 1**: Process PDFs in the "documents" folder
```bash
python stamp_pdf.py ./documents
```
Output will be saved to: `./documents/stamped_pdfs/`

**Example 2**: Process PDFs with custom output
```bash
python stamp_pdf.py ./documents ./processed_documents
```
Output will be saved to: `./processed_documents/`

## How It Works

1. **Scans** the input folder for all PDF files
2. **Counts** the number of pages in each PDF (variable N)
3. **Creates** a custom stamp featuring:
   - Red rounded rectangle border
   - "Received and Reviewed N Pages" text in bold (where N is the page count)
   - Two decorative red lines
4. **Applies** the stamp to the **first page only** of each PDF
5. **Saves** stamped PDFs with "stamped_" prefix to the output folder

## Output

- Stamped PDFs are saved with the prefix `stamped_` followed by the original filename
- Original files are not modified
- Processing summary is displayed after completion

## Example Output

```
============================================================
PDF Stamping Tool
============================================================

Found 3 PDF file(s) to process.

Processing: document1.pdf
  Pages: 5
  ✓ Stamped PDF saved to: ./stamped_pdfs/stamped_document1.pdf

Processing: document2.pdf
  Pages: 12
  ✓ Stamped PDF saved to: ./stamped_pdfs/stamped_document2.pdf

Processing: document3.pdf
  Pages: 3
  ✓ Stamped PDF saved to: ./stamped_pdfs/stamped_document3.pdf

============================================================
Processing Summary
============================================================
Total files found:    3
Successfully stamped: 3
Failed:              0
Skipped:             0
============================================================
```

## Stamp Design

The stamp includes:
- **Round Red Box**: Rectangle with rounded corners (200x75 pixels)
- **Header Text**: "Received and Reviewed N Pages" in bold (where N is the page count)
- **Line 1**: Solid red horizontal line
- **Line 2**: Solid red horizontal line

The stamp is positioned to overlay on the **first page only** of the PDF.

## Error Handling

- Skips files that cannot be read or are empty
- Displays error messages for failed operations
- Continues processing remaining files if one fails
- Provides detailed summary at the end

## Requirements

- Python 3.7+
- PyPDF2 3.0.1
- reportlab 4.0.7

## Troubleshooting

**Issue**: "No PDF files found"
- Ensure your input folder contains PDF files with `.pdf` extension

**Issue**: "Permission denied" errors
- Check that you have read permissions for input files
- Check that you have write permissions for the output folder

**Issue**: Import errors
- Make sure all dependencies are installed: `pip install -r requirements.txt`

## License

This is a utility tool for PDF processing. Use it freely for your document management needs.

