import os
try:
    from fpdf import FPDF
except ImportError:
    from fpdf2 import FPDF

class MarkdownPDF(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

def sanitize_text_for_pdf(text: str) -> str:
    # Replace common unicode characters that are not in Latin-1
    replacements = {
        '\u2019': "'",
        '\u2018': "'",
        '\u201c': '"',
        '\u201d': '"',
        '\u2013': '-',
        '\u2014': '-',
        '\u2265': '>=',
        '\u2264': '<=',
        '\u2192': '->',
        '\u2022': '*',
    }
    for orig, rep in replacements.items():
        text = text.replace(orig, rep)
    # Encode as latin-1, replacing unmappable characters with a placeholder
    return text.encode('latin-1', 'replace').decode('latin-1')

def convert_markdown_to_pdf_bytes(markdown_text: str, title: str = "Research Report") -> bytes:
    pdf = MarkdownPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # Process lines
    lines = markdown_text.split("\n")
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            pdf.ln(3)
            continue
            
        # Clean inline markdown markers for cleaner reading
        clean_line = stripped
        clean_line = clean_line.replace("**", "")
        clean_line = clean_line.replace("*", "")
        clean_line = clean_line.replace("`", "")
        clean_line = sanitize_text_for_pdf(clean_line)
            
        # Headings
        if stripped.startswith("# "):
            title_text = clean_line[2:].strip()
            pdf.set_font("helvetica", "B", 18)
            pdf.set_text_color(24, 24, 27) # Dark zinc
            pdf.ln(5)
            pdf.multi_cell(0, 8, title_text)
            pdf.ln(3)
        elif stripped.startswith("## "):
            h1_text = clean_line[3:].strip()
            pdf.set_font("helvetica", "B", 13)
            pdf.set_text_color(39, 39, 42)
            pdf.ln(4)
            pdf.multi_cell(0, 7, h1_text)
            pdf.ln(2)
        elif stripped.startswith("### "):
            h2_text = clean_line[4:].strip()
            pdf.set_font("helvetica", "B", 10)
            pdf.set_text_color(63, 63, 70)
            pdf.ln(3)
            pdf.multi_cell(0, 6, h2_text)
            pdf.ln(1)
        elif stripped.startswith("- ") or stripped.startswith("* "):
            bullet_text = clean_line[2:].strip()
            pdf.set_font("helvetica", "", 9.5)
            pdf.set_text_color(63, 63, 70)
            # Indent bullet point slightly
            current_x = pdf.get_x()
            pdf.set_x(current_x + 10)
            pdf.cell(5, 5, chr(149), ln=0) # Bullet symbol
            pdf.multi_cell(0, 5, bullet_text)
            pdf.set_x(current_x)
        elif stripped.startswith("1. ") or stripped.startswith("2. ") or stripped.startswith("3. ") or stripped.startswith("4. ") or stripped.startswith("5. ") or stripped.startswith("6. ") or stripped.startswith("7. ") or stripped.startswith("8. ") or stripped.startswith("9. "):
            parts = clean_line.split(".", 1)
            num = parts[0].strip() + "."
            text = parts[1].strip()
            pdf.set_font("helvetica", "", 9.5)
            pdf.set_text_color(63, 63, 70)
            current_x = pdf.get_x()
            pdf.set_x(current_x + 10)
            pdf.cell(8, 5, num, ln=0)
            pdf.multi_cell(0, 5, text)
            pdf.set_x(current_x)
        else:
            pdf.set_font("helvetica", "", 9.5)
            pdf.set_text_color(63, 63, 70)
            pdf.multi_cell(0, 5, clean_line)
            pdf.ln(1.5)
            
    # Output to bytes
    return bytes(pdf.output())
