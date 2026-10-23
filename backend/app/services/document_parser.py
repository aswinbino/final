"""
Document Parser Service (Module 1)
Handles PDF and DOCX parsing with text extraction and preprocessing.
"""

import re
import os
from pathlib import Path
from typing import Tuple, List, Dict, Any, Optional
from loguru import logger


class DocumentParser:
    """Parses PDF and DOCX files, extracting structured text."""

    SUPPORTED_TYPES = {".pdf", ".docx", ".doc", ".txt"}

    @staticmethod
    def detect_file_type(filename: str) -> str:
        suffix = Path(filename).suffix.lower()
        if suffix not in DocumentParser.SUPPORTED_TYPES:
            # Default to .txt if unknown
            return ".txt"
        return suffix

    @staticmethod
    def parse(file_path: str, filename: str) -> Dict[str, Any]:
        """
        Parse a document and return structured text data.
        """
        file_type = DocumentParser.detect_file_type(filename)
        
        try:
            if file_type == ".pdf":
                try:
                    return DocumentParser._parse_pdf(file_path)
                except Exception as pdf_err:
                    logger.warning(f"PyMuPDF failed ({pdf_err}), attempting direct text read fallback...")
                    return DocumentParser._parse_txt(file_path)
            elif file_type in (".docx", ".doc"):
                try:
                    return DocumentParser._parse_docx(file_path)
                except Exception as docx_err:
                    logger.warning(f"DOCX parser failed ({docx_err}), attempting direct text read fallback...")
                    return DocumentParser._parse_txt(file_path)
            else:
                return DocumentParser._parse_txt(file_path)
        except Exception as e:
            logger.error(f"Failed to parse document {filename}: {e}")
            raise RuntimeError(f"Could not parse document: {str(e)}")

    @staticmethod
    def _parse_txt(file_path: str) -> Dict[str, Any]:
        """Read plain text document directly."""
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            raw_text = f.read()
        raw_text = DocumentParser._clean_text(raw_text)
        estimated_pages = max(1, len(raw_text) // 3000)
        return {
            "raw_text": raw_text,
            "page_count": estimated_pages,
            "pages": [{"page_number": 1, "text": raw_text}],
            "file_type": "txt",
        }

    @staticmethod
    def _parse_pdf(file_path: str) -> Dict[str, Any]:
        """Parse PDF using PyMuPDF (fitz)."""
        try:
            import fitz  # PyMuPDF
        except ImportError:
            raise ImportError("PyMuPDF not installed. Run: pip install pymupdf")

        doc = fitz.open(file_path)
        pages = []
        full_text_parts = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            text = DocumentParser._clean_text(text)
            pages.append({"page_number": page_num + 1, "text": text})
            full_text_parts.append(text)

        doc.close()
        raw_text = "\n\n".join(full_text_parts)

        return {
            "raw_text": raw_text,
            "page_count": len(pages),
            "pages": pages,
            "file_type": "pdf",
        }

    @staticmethod
    def _parse_docx(file_path: str) -> Dict[str, Any]:
        """Parse DOCX using python-docx or native zipfile/xml parser."""
        try:
            from docx import Document
            doc = Document(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            raw_text = "\n\n".join(paragraphs)
        except Exception:
            # Native fallback using zipfile and xml without external dependencies
            import zipfile
            import xml.etree.ElementTree as ET
            paragraphs = []
            try:
                with zipfile.ZipFile(file_path) as docx_zip:
                    xml_content = docx_zip.read('word/document.xml')
                    tree = ET.fromstring(xml_content)
                    # XML namespaces
                    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
                    for p in tree.iterfind('.//w:p', ns):
                        texts = [node.text for node in p.iterfind('.//w:t', ns) if node.text]
                        if texts:
                            paragraphs.append(''.join(texts))
                    raw_text = "\n\n".join(paragraphs)
            except Exception as e:
                # Fallback to plain binary decode
                with open(file_path, 'rb') as f:
                    content = f.read()
                    raw_text = re.sub(r'[^\x20-\x7E\n\t]', ' ', content.decode('utf-8', errors='ignore'))

        raw_text = DocumentParser._clean_text(raw_text)
        estimated_pages = max(1, len(raw_text) // 3000)

        return {
            "raw_text": raw_text,
            "page_count": estimated_pages,
            "pages": [{"page_number": 1, "text": raw_text}],
            "file_type": "docx",
        }

    @staticmethod
    def _clean_text(text: str) -> str:
        """Remove noise, normalize whitespace, fix common PDF artifacts."""
        if not text:
            return ""
        # Remove null bytes and control chars (except newlines/tabs)
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
        # Collapse multiple spaces/tabs to single space
        text = re.sub(r"[ \t]+", " ", text)
        # Normalize multiple newlines
        text = re.sub(r"\n{3,}", "\n\n", text)
        # Remove page numbers (lone digits on a line)
        text = re.sub(r"^\s*\d+\s*$", "", text, flags=re.MULTILINE)
        # Strip leading/trailing whitespace
        text = text.strip()
        return text

    @staticmethod
    def segment_into_clauses(raw_text: str, pages: List[Dict]) -> List[Dict[str, Any]]:
        """
        Segment document text into individual clauses.
        Uses heading patterns and double-newline paragraph breaks.
        """
        # Build a char-to-page map for evidence grounding
        char_offset = 0
        char_page_map = []
        for p in pages:
            page_text = p["text"]
            for _ in page_text:
                char_page_map.append(p["page_number"])
            char_offset += len(page_text) + 2  # +2 for \n\n

        # Split on numbered clauses, headings, or double newlines
        clause_patterns = [
            # Numbered sections: "1.", "1.1", "SECTION 1", "Article 1"
            r"(?=^(?:SECTION|Article|Clause|Schedule|Exhibit)\s+\d+|\d+\.\s+[A-Z])",
            # Headed clauses: All-caps heading followed by content
            r"(?=^[A-Z][A-Z\s]{5,}:?\s*$)",
        ]

        combined_pattern = "|".join(clause_patterns)
        parts = re.split(combined_pattern, raw_text, flags=re.MULTILINE)

        # Filter very short fragments
        clauses = []
        start_char = 0
        for idx, part in enumerate(parts):
            part = part.strip()
            if len(part) < 30:
                start_char += len(part)
                continue

            end_char = start_char + len(part)
            # Determine page number from first character
            page_num = char_page_map[min(start_char, len(char_page_map) - 1)] if char_page_map else 1

            clauses.append({
                "index": len(clauses),
                "raw_text": part,
                "cleaned_text": DocumentParser._clean_text(part),
                "page_number": page_num,
                "start_char": start_char,
                "end_char": end_char,
            })
            start_char = end_char + 1

        # If no structured splits found, fall back to paragraph breaks
        if len(clauses) < 2:
            paragraphs = [p.strip() for p in raw_text.split("\n\n") if len(p.strip()) >= 30]
            clauses = [
                {
                    "index": i,
                    "raw_text": para,
                    "cleaned_text": DocumentParser._clean_text(para),
                    "page_number": 1,
                    "start_char": 0,
                    "end_char": len(para),
                }
                for i, para in enumerate(paragraphs)
            ]

        logger.info(f"Segmented {len(clauses)} clauses from document.")
        return clauses
