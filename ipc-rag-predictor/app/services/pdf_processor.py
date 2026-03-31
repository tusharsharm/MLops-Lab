import fitz  # PyMuPDF
import re
from typing import List, Dict
import structlog
from pathlib import Path

logger = structlog.get_logger()

class PDFProcessor:
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)

    def extract_sections(self) -> List[Dict]:
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"IPC PDF not found at {self.pdf_path}")

        logger.info("Starting PDF extraction", pdf_path=str(self.pdf_path))
        doc = fitz.open(self.pdf_path)
        sections = []
        current_section = None
        current_text = []

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text("text")

            # Detect IPC section headers (e.g., "Section 302", "302. Punishment for murder")
            section_pattern = r'(?:Section\s+)?(\d+[A-Za-z]*)\.?\s*(.+?)(?=\n(?:Section\s+)?\d+[A-Za-z]*\.|\Z)'
            matches = re.finditer(section_pattern, text, re.MULTILINE | re.DOTALL)

            for match in matches:
                section_num = match.group(1).strip()
                title = match.group(2).strip() if match.group(2) else ""

                if current_section and current_text:
                    sections.append({
                        "section": current_section,
                        "title": title,
                        "content": " ".join(current_text).strip()
                    })

                current_section = section_num
                current_text = [text[match.end():].strip()]

            if current_section:
                current_text.append(text)

        # Add the last section
        if current_section and current_text:
            sections.append({
                "section": current_section,
                "title": "",
                "content": " ".join(current_text).strip()
            })

        logger.info(f"Extracted {len(sections)} IPC sections")
        return sections