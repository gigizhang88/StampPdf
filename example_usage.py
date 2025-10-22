"""
Example usage script for the PDF Stamping Tool
This script demonstrates how to use the stamp_pdf module programmatically.
"""

from stamp_pdf import count_pdf_pages, create_stamp, apply_stamp_to_pdf, batch_process_pdfs
import os


def example_single_pdf():
    """Example: Process a single PDF file"""
    print("Example 1: Processing a single PDF file")
    print("-" * 50)
    
    pdf_file = "sample.pdf"
    
    if not os.path.exists(pdf_file):
        print(f"Error: {pdf_file} not found. Please provide a sample PDF.")
        return
    
    # Count pages
    page_count = count_pdf_pages(pdf_file)
    print(f"Pages in {pdf_file}: {page_count}")
    
    # Create stamp
    stamp = create_stamp(page_count)
    
    # Apply stamp
    output_file = "stamped_sample.pdf"
    success = apply_stamp_to_pdf(pdf_file, output_file, stamp)
    
    if success:
        print(f"Success! Stamped PDF saved as: {output_file}")
    else:
        print("Failed to process PDF")
    
    print()


def example_batch_processing():
    """Example: Batch process multiple PDFs"""
    print("Example 2: Batch processing multiple PDFs")
    print("-" * 50)
    
    input_folder = "./test_pdfs"
    output_folder = "./output_pdfs"
    
    if not os.path.exists(input_folder):
        print(f"Error: {input_folder} not found. Please create it and add some PDFs.")
        return
    
    # Batch process
    stats = batch_process_pdfs(input_folder, output_folder)
    
    print(f"\nProcessed: {stats['processed']} / {stats['total_files']} files")
    print()


def example_custom_stamp():
    """Example: Create a custom stamp with specific dimensions"""
    print("Example 3: Creating a custom stamp")
    print("-" * 50)
    
    # Create stamp for a 10-page document with custom size
    page_count = 10
    stamp = create_stamp(page_count, width=250, height=150)
    
    print(f"Created custom stamp: 'Received and Reviewed {page_count} Pages'")
    print("Stamp dimensions: 250x150 pixels")
    print("Note: Stamp will only be applied to the first page of the PDF")
    print()


if __name__ == "__main__":
    print("=" * 50)
    print("PDF Stamping Tool - Example Usage")
    print("=" * 50)
    print()
    
    # Uncomment the examples you want to run:
    
    # example_single_pdf()
    # example_batch_processing()
    example_custom_stamp()
    
    print("\nNote: Uncomment the examples in the script to run them.")
    print("Make sure you have sample PDF files in the appropriate locations.")

