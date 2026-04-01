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
        current_title = None
        current_text: List[str] = []

        # Detect IPC section headers (e.g., "Section 302", "302. Punishment for murder")
        section_pattern = r'(?:Section\s+)?(\d+[A-Za-z]*)\.?\s*(.+?)(?=\n(?:Section\s+)?\d+[A-Za-z]*\.|\Z)'

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text("text")

            matches = list(re.finditer(section_pattern, text, re.MULTILINE | re.DOTALL))

            if matches:
                for match in matches:
                    section_num = match.group(1).strip()
                    title = match.group(2).strip() if match.group(2) else ""

                    # If we were collecting a previous section, save it using its stored title
                    if current_section is not None and current_text:
                        sections.append({
                            "section": current_section,
                            "title": current_title or "",
                            "content": " ".join(current_text).strip()
                        })

                    # Start a new section from the current match
                    current_section = section_num
                    current_title = title
                    # Start section text from the remainder of the page after the match
                    current_text = [text[match.end():].strip()]

                # do not append the whole page again (we already captured the remainder)
            else:
                # No section header on this page; append page text to current section (if any)
                if current_section is not None:
                    current_text.append(text)

        # Add the last section if present
        if current_section is not None and current_text:
            sections.append({
                "section": current_section,
                "title": current_title or "",
                "content": " ".join(current_text).strip()
            })

        logger.info(f"Extracted {len(sections)} IPC sections")
        return sections