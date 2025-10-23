"""
PDF Stamping Tool
Batch processes PDF documents by adding a custom stamp with page count information.
"""

import os
import sys
from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import red

# Optional: use PyMuPDF (fitz) to detect text blocks and find low-overlap placement
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except Exception:
    PYMUPDF_AVAILABLE = False


def count_pdf_pages(pdf_path):
    """
    Count the number of pages in a PDF document.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        int: Number of pages in the PDF
    """
    try:
        reader = PdfReader(pdf_path)
        return len(reader.pages)
    except Exception as e:
        print(f"Error counting pages in {pdf_path}: {e}")
        return 0


def create_stamp(page_count, width=260, height=180):
    """
    Create a stamp with a round red box, text, and red lines.
    
    Args:
        page_count (int): Number of pages (N) to display on stamp
        width (int): Width of the stamp
        height (int): Height of the stamp
        
    Returns:
        BytesIO: PDF stamp as bytes
    """
    # Create a buffer for the stamp PDF
    buffer = BytesIO()
    
    # Create canvas
    c = canvas.Canvas(buffer, pagesize=(width, height))
    
    # Set up dimensions
    center_x = width / 2
    top_y = height - 20
    
    # Draw round red box (rectangle with rounded corners)
    c.setStrokeColor(red)
    c.setFillColor(red)
    # thinner stroke for box outline
    c.setLineWidth(1.2)
    
    # Rounded rectangle for the box (reduce width ~85% of previous)
    box_width = (width - 30) * 0.85
    box_height = 140
    box_x = center_x - box_width / 2
    box_y = top_y - box_height
    radius = 10
    
    c.roundRect(box_x, box_y, box_width, box_height, radius, stroke=1, fill=0)
    
    # Add text "Received and Reviewed N Pages"
    c.setFillColor(red)
    # Two-line text: header then N Pages on new line
    c.setFont("Helvetica-Bold", 11)
    header = "Received and Reviewed"
    header_w = c.stringWidth(header, "Helvetica-Bold", 11)
    header_y = top_y - 24
    c.drawString(center_x - header_w / 2, header_y, header)

    c.setFont("Helvetica-Bold", 11)
    pages_line = f"{page_count} Pages"
    pages_w = c.stringWidth(pages_line, "Helvetica-Bold", 11)
    pages_y = header_y - 16
    c.drawString(center_x - pages_w / 2, pages_y, pages_line)
    
    # First solid red line (keep strong spacing below text)
    line_y1 = pages_y - 36
    c.setStrokeColor(red)
    # keep bold, but inset slightly from the box
    c.setLineWidth(2.5)
    inner_margin = 8
    c.line(box_x + inner_margin, line_y1, box_x + box_width - inner_margin, line_y1)
    
    # Second solid red line – close to the first line, not the box
    line_y2 = line_y1 - 16
    c.line(box_x + inner_margin, line_y2, box_x + box_width - inner_margin, line_y2)
    
    # Finalize the PDF
    c.save()
    buffer.seek(0)
    
    return buffer


def create_overlay_stamp(page_width, page_height, page_count, pos_x, pos_y, rotation_deg,
                         stamp_width=260, stamp_height=180):
    """
    Create a full-page transparent overlay PDF with the stamp drawn at (pos_x, pos_y),
    rotated to stay visually upright (counter to page rotation).

    Returns: BytesIO buffer of a single-page PDF sized to the target page.
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=(page_width, page_height))
    c.setFillAlpha(0)
    c.setStrokeAlpha(1)

    # Prepare to draw stamp upright relative to viewer
    c.saveState()
    c.translate(pos_x, pos_y)
    if rotation_deg:
        c.rotate(-rotation_deg)

    # Draw the same stamp as create_stamp but at origin (0,0)
    center_x = stamp_width / 2
    top_y = stamp_height - 20

    c.setStrokeColor(red)
    c.setFillColor(red)
    # thinner stroke for box outline
    c.setLineWidth(1.2)
    c.setLineWidth(2.0)

    box_width = (stamp_width - 30) * 0.85
    box_height = 140
    box_x = center_x - box_width / 2
    box_y = top_y - box_height
    radius = 10
    c.roundRect(box_x, box_y, box_width, box_height, radius, stroke=1, fill=0)

    c.setFillColor(red)
    # Two-line text
    c.setFont("Helvetica-Bold", 11)
    header = "Received and Reviewed"
    header_w = c.stringWidth(header, "Helvetica-Bold", 11)
    header_y = top_y - 24
    c.drawString(center_x - header_w / 2, header_y, header)

    c.setFont("Helvetica-Bold", 11)
    pages_line = f"{page_count} Pages"
    pages_w = c.stringWidth(pages_line, "Helvetica-Bold", 11)
    pages_y = header_y - 16
    c.drawString(center_x - pages_w / 2, pages_y, pages_line)

    # Lines with increased spacing
    line_y1 = pages_y - 36
    c.setStrokeColor(red)
    # keep bold, but inset slightly from the box
    c.setLineWidth(2.5)
    inner_margin = 8
    c.line(box_x + inner_margin, line_y1, box_x + box_width - inner_margin, line_y1)

    # Second line closer to the first line, not the box
    line_y2 = line_y1 - 36
    c.line(box_x + inner_margin, line_y2, box_x + box_width - inner_margin, line_y2)

    c.restoreState()

    c.save()
    buffer.seek(0)
    return buffer


def _map_viewer_to_page_coords(x_v, y_v, page_width, page_height, rotation_deg):
    """Map viewer-space coords (rotation-normalized) to PDF page coordinates."""
    r = (rotation_deg or 0) % 360
    if r == 0:
        return x_v, y_v
    if r == 90:
        # viewer(x,y) = (h - y_p, x_p) => inverse: x_p = y_v, y_p = page_height - x_v
        return y_v, page_height - x_v
    if r == 180:
        # viewer(x,y) = (w - x_p, h - y_p) => inverse: x_p = w - x_v, y_p = h - y_v
        return page_width - x_v, page_height - y_v
    if r == 270:
        # viewer(x,y) = (y_p, w - x_p) => inverse: x_p = w - y_v, y_p = x_v
        return page_width - y_v, x_v
    return x_v, y_v

def _map_page_to_viewer_coords(x_p, y_p, page_width, page_height, rotation_deg):
    """Map PDF page coordinates to viewer-space coords (normalized orientation)."""
    r = (rotation_deg or 0) % 360
    if r == 0:
        return x_p, y_p
    if r == 90:
        return page_height - y_p, x_p
    if r == 180:
        return page_width - x_p, page_height - y_p
    if r == 270:
        return y_p, page_width - x_p
    return x_p, y_p

def _choose_stamp_position(input_pdf_path, page_index, page_width, page_height, stamp_w, stamp_h, rotation_deg, margin=12):
    """Choose a placement with minimal text overlap using PyMuPDF if available, else corners.
    Returns (x_page, y_page) in PDF page coordinates (unrotated page space) and rotation compensation in degrees.
    """
    # Define candidate positions in viewer space (after considering rotation for visual orientation)
    view_w = page_height if (rotation_deg % 180 == 90) else page_width
    view_h = page_width if (rotation_deg % 180 == 90) else page_height
    candidates_view = [
        (view_w - margin - stamp_w, view_h - margin - stamp_h),  # top-right
        (margin, view_h - margin - stamp_h),                     # top-left
        (view_w - margin - stamp_w, margin),                     # bottom-right
        (margin, margin),                                        # bottom-left
    ]

    # If PyMuPDF is available, scan for the largest whitespace area that fits the stamp
    if PYMUPDF_AVAILABLE:
        try:
            with fitz.open(input_pdf_path) as doc:
                page = doc.load_page(page_index)
                # Prefer word-level rectangles; fallback to blocks
                words = page.get_text("words") or []  # each: (x0,y0,x1,y1, word, ...)
                src_rects = words if words else (page.get_text("blocks") or [])
                text_rects = []
                pad = 3.0
                for r in src_rects:
                    px0, py0, px1, py1 = float(r[0]), float(r[1]), float(r[2]), float(r[3])
                    vx0, vy0 = _map_page_to_viewer_coords(px0, py0, page_width, page_height, rotation_deg)
                    vx1, vy1 = _map_page_to_viewer_coords(px1, py1, page_width, page_height, rotation_deg)
                    x0, x1 = min(vx0, vx1) - pad, max(vx0, vx1) + pad
                    y0, y1 = min(vy0, vy1) - pad, max(vy0, vy1) + pad
                    x0 = max(0.0, x0); y0 = max(0.0, y0)
                    x1 = min(view_w, x1); y1 = min(view_h, y1)
                    if x1 > x0 and y1 > y0:
                        text_rects.append((x0, y0, x1, y1))

                def rect_overlap(ax0, ay0, ax1, ay1, bx0, by0, bx1, by1):
                    dx = max(0.0, min(ax1, bx1) - max(ax0, bx0))
                    dy = max(0.0, min(ay1, by1) - max(ay0, by0))
                    return dx * dy

                def any_overlap(ax0, ay0, ax1, ay1):
                    for (bx0, by0, bx1, by1) in text_rects:
                        if rect_overlap(ax0, ay0, ax1, ay1, bx0, by0, bx1, by1) > 0.0:
                            return True
                    return False

                def clearance(ax0, ay0, ax1, ay1):
                    left_clear = ax0
                    right_clear = view_w - ax1
                    top_clear = ay0
                    bottom_clear = view_h - ay1
                    edge_min = min(left_clear, right_clear, top_clear, bottom_clear)
                    min_text = float("inf")
                    for (bx0, by0, bx1, by1) in text_rects:
                        dx = 0.0
                        if ax1 <= bx0:
                            dx = bx0 - ax1
                        elif bx1 <= ax0:
                            dx = ax0 - bx1
                        dy = 0.0
                        if ay1 <= by0:
                            dy = by0 - ay1
                        elif by1 <= ay0:
                            dy = ay0 - by1
                        d = min(dx, dy)
                        if d < min_text:
                            min_text = d
                    if min_text == float("inf"):
                        min_text = edge_min
                    return min(edge_min, min_text)

                # If still no text rects (e.g., empty or image-only), place near bottom-left
                if not text_rects:
                    xv = margin
                    yv = margin
                    xp, yp = _map_viewer_to_page_coords(xv, yv, page_width, page_height, rotation_deg)
                    return xp, yp

                best = None  # (score, xv, yv)
                step = max(6.0, min(stamp_w, stamp_h) / 14.0)
                y = margin
                max_y = max(margin, view_h - margin - stamp_h)
                while y <= max_y:
                    x = margin
                    max_x = max(margin, view_w - margin - stamp_w)
                    while x <= max_x:
                        ax0, ay0, ax1, ay1 = x, y, x + stamp_w, y + stamp_h
                        if not any_overlap(ax0, ay0, ax1, ay1):
                            c = clearance(ax0, ay0, ax1, ay1)
                            if (best is None) or (c > best[0]):
                                best = (c, x, y)
                        x += step
                    y += step

                # If no zero-overlap location from text geometry, use raster scan to minimize ink density
                if best is None:
                    try:
                        # Render a downscaled pixmap and build an integral image of non-white pixels
                        target_w = 900
                        scale = max(0.5, min(3.0, target_w / max(1.0, float(page.rect.width))))
                        pm = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
                        pw, ph, n = pm.width, pm.height, pm.n  # n: number of components
                        samples = pm.samples  # bytes

                        # Helper to compute brightness; treat near-white as empty
                        def is_ink(idx):
                            if n == 1:
                                v = samples[idx]
                                return 1 if v < 240 else 0
                            # assume RGB
                            r = samples[idx]
                            g = samples[idx + 1]
                            b = samples[idx + 2]
                            # simple luminance
                            lum = (299 * r + 587 * g + 114 * b) // 1000
                            return 1 if lum < 240 else 0

                        # Build integral image
                        import array
                        I = [array.array('I', [0] * (pw + 1))]
                        for ypix in range(ph):
                            row = array.array('I', [0])
                            rowsum = 0
                            base = ypix * pw * n
                            for xpix in range(pw):
                                rowsum += is_ink(base + xpix * n)
                                row.append(rowsum + I[ypix][xpix + 1])
                            I.append(row)

                        # map viewer coords to pix coords
                        sx = pw / max(1.0, view_w)
                        sy = ph / max(1.0, view_h)

                        def ink_sum(x0v, y0v, x1v, y1v):
                            x0 = max(0, min(pw, int(x0v * sx)))
                            y0 = max(0, min(ph, int(y0v * sy)))
                            x1 = max(0, min(pw, int(x1v * sx)))
                            y1 = max(0, min(ph, int(y1v * sy)))
                            if x1 <= x0 or y1 <= y0:
                                return 1e9
                            return I[y1][x1] - I[y0][x1] - I[y1][x0] + I[y0][x0]

                        best_pix = None  # (ink, xv, yv)
                        y = margin
                        while y <= max_y:
                            x = margin
                            while x <= max_x:
                                ink = ink_sum(x, y, x + stamp_w, y + stamp_h)
                                if (best_pix is None) or (ink < best_pix[0]):
                                    best_pix = (ink, x, y)
                                x += step
                            y += step
                        if best_pix is not None:
                            _, xv, yv = best_pix
                            xp, yp = _map_viewer_to_page_coords(xv, yv, page_width, page_height, rotation_deg)
                            return xp, yp
                    except Exception:
                        pass

                if best is not None:
                    _, xv, yv = best
                    xp, yp = _map_viewer_to_page_coords(xv, yv, page_width, page_height, rotation_deg)
                    return xp, yp
        except Exception:
            pass

    # Fallback: choose corner with least overlap if possible, else bottom-right
    xv, yv = candidates_view[2]
    try:
        if PYMUPDF_AVAILABLE:
            with fitz.open(input_pdf_path) as doc:
                page = doc.load_page(page_index)
                blocks = page.get_text("blocks") or []
                text_rects = []
                for b in blocks:
                    px0, py0, px1, py1 = float(b[0]), float(b[1]), float(b[2]), float(b[3])
                    vx0, vy0 = _map_page_to_viewer_coords(px0, py0, page_width, page_height, rotation_deg)
                    vx1, vy1 = _map_page_to_viewer_coords(px1, py1, page_width, page_height, rotation_deg)
                    x0, x1 = min(vx0, vx1), max(vx0, vx1)
                    y0, y1 = min(vy0, vy1), max(vy0, vy1)
                    text_rects.append((x0, y0, x1, y1))

                # If no text found on page, prefer bottom-left large whitespace
                if not text_rects:
                    xv = max(margin, min(view_w - margin - stamp_w, margin))
                    yv = max(margin, min(view_h - margin - stamp_h, margin))
                    xp, yp = _map_viewer_to_page_coords(xv, yv, page_width, page_height, rotation_deg)
                    return xp, yp
                def ov(ax0, ay0, ax1, ay1, bx0, by0, bx1, by1):
                    dx = max(0.0, min(ax1, bx1) - max(ax0, bx0))
                    dy = max(0.0, min(ay1, by1) - max(ay0, by0))
                    return dx * dy
                best_idx, best_score = 0, float("inf")
                for i, (cx, cy) in enumerate(candidates_view):
                    ax0, ay0, ax1, ay1 = cx, cy, cx + stamp_w, cy + stamp_h
                    s = 0.0
                    for (bx0, by0, bx1, by1) in text_rects:
                        s += ov(ax0, ay0, ax1, ay1, bx0, by0, bx1, by1)
                    # Tie-breaker: prefer bottom-right (index 2) when scores are equal
                    if (s < best_score) or (s == best_score and i == 2):
                        best_idx, best_score = i, s
                xv, yv = candidates_view[best_idx]
    except Exception:
        pass

    xp, yp = _map_viewer_to_page_coords(xv, yv, page_width, page_height, rotation_deg)
    return xp, yp


def apply_stamp_to_pdf(input_pdf_path, output_pdf_path, page_count):
    """
    Apply the stamp to the first page of a PDF document.
    
    Args:
        input_pdf_path (str): Path to the input PDF
        output_pdf_path (str): Path to save the stamped PDF
        stamp_buffer (BytesIO): Stamp PDF as bytes
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Read the input PDF
        reader = PdfReader(input_pdf_path)
        writer = PdfWriter()
        
        # Stamp dimensions (must match overlay drawing)
        stamp_w = 260.0
        stamp_h = 180.0
        
        # Apply stamp only to the first page
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            
            # Only apply stamp to the first page (page_num == 0)
            if page_num == 0:
                # Page size and rotation
                page_w = float(page.mediabox.width)
                page_h = float(page.mediabox.height)
                try:
                    rotation = int(getattr(page, "rotation", 0) or 0)
                except Exception:
                    rotation = 0

                # Choose position that minimizes overlap with text where possible
                margin = 12
                tx, ty = _choose_stamp_position(
                    input_pdf_path, page_num, page_w, page_h, stamp_w, stamp_h, rotation, margin
                )

                # Draw overlay and merge (works with PyPDF2 when merge_transformed_page is unavailable)
                overlay_buf = create_overlay_stamp(page_w, page_h, page_count, tx, ty, rotation, stamp_w, stamp_h)
                overlay_pdf = PdfReader(overlay_buf)
                overlay_page = overlay_pdf.pages[0]
                page.merge_page(overlay_page)
            
            writer.add_page(page)
        
        # Write the output PDF
        with open(output_pdf_path, 'wb') as output_file:
            writer.write(output_file)
        
        return True
    except Exception as e:
        print(f"Error applying stamp to {input_pdf_path}: {e}")
        return False


def batch_process_pdfs(input_folder, output_folder=None):
    """
    Batch process all PDF files in a folder.
    
    Args:
        input_folder (str): Folder containing input PDFs
        output_folder (str): Folder to save stamped PDFs (optional)
        
    Returns:
        dict: Statistics about the processing
    """
    # If no output folder specified, create one in the input folder
    if output_folder is None:
        output_folder = os.path.join(input_folder, "stamped_pdfs")
    
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Statistics
    stats = {
        'total_files': 0,
        'processed': 0,
        'failed': 0,
        'skipped': 0
    }
    
    # Get all PDF files in the input folder
    pdf_files = [f for f in os.listdir(input_folder) 
                 if f.lower().endswith('.pdf') and os.path.isfile(os.path.join(input_folder, f))]
    
    if not pdf_files:
        print(f"No PDF files found in {input_folder}")
        return stats
    
    stats['total_files'] = len(pdf_files)
    print(f"Found {len(pdf_files)} PDF file(s) to process.\n")
    
    # Process each PDF
    for pdf_file in pdf_files:
        input_path = os.path.join(input_folder, pdf_file)
        output_path = os.path.join(output_folder, f"stamped_{pdf_file}")
        
        print(f"Processing: {pdf_file}")
        
        # Count pages
        N = count_pdf_pages(input_path)
        
        if N == 0:
            print(f"  ⚠ Skipped (could not read PDF or empty)")
            stats['skipped'] += 1
            continue
        
        print(f"  Pages: {N}")
        
        # Apply stamp to PDF (first page only)
        success = apply_stamp_to_pdf(input_path, output_path, N)
        
        if success:
            print(f"  ✓ Stamped PDF saved to: {output_path}")
            stats['processed'] += 1
        else:
            print(f"  ✗ Failed to process")
            stats['failed'] += 1
        
        print()
    
    return stats


def main():
    """Main entry point for the script."""
    print("=" * 60)
    print("PDF Stamping Tool")
    print("=" * 60)
    print()
    
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python stamp_pdf.py <input_folder> [output_folder]")
        print()
        print("Arguments:")
        print("  input_folder  : Folder containing PDF files to process")
        print("  output_folder : (Optional) Folder to save stamped PDFs")
        print("                  If not specified, creates 'stamped_pdfs' subfolder")
        print()
        print("Example:")
        print("  python stamp_pdf.py ./documents")
        print("  python stamp_pdf.py ./documents ./output")
        sys.exit(1)
    
    input_folder = sys.argv[1]
    output_folder = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Check if input folder exists
    if not os.path.exists(input_folder):
        print(f"Error: Input folder '{input_folder}' does not exist.")
        sys.exit(1)
    
    if not os.path.isdir(input_folder):
        print(f"Error: '{input_folder}' is not a directory.")
        sys.exit(1)
    
    # Process PDFs
    stats = batch_process_pdfs(input_folder, output_folder)
    
    # Print summary
    print("=" * 60)
    print("Processing Summary")
    print("=" * 60)
    print(f"Total files found:    {stats['total_files']}")
    print(f"Successfully stamped: {stats['processed']}")
    print(f"Failed:              {stats['failed']}")
    print(f"Skipped:             {stats['skipped']}")
    print("=" * 60)


if __name__ == "__main__":
    main()

