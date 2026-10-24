"""
Document Parser Service (Module 1: Document Upload & Ingestion Status)
Handles PDF (PyMuPDF) and DOCX (python-docx) parsing with page mapping,
section header retention, and paragraph boundary preservation.
"""

import re
import os
from pathlib import Path
from typing import Tuple, List, Dict, Any, Optional
from loguru import logger


class DocumentParser:
    """Parses PDF and DOCX files, extracting structured text with exact page provenance."""

    SUPPORTED_TYPES = {".pdf", ".docx", ".doc", ".txt"}

    @staticmethod
    def detect_file_type(filename: str) -> str:
        suffix = Path(filename).suffix.lower()
        if suffix not in DocumentParser.SUPPORTED_TYPES:
            return ".txt"
        return suffix

    @staticmethod
    def parse(file_path: str, filename: str) -> Dict[str, Any]:
        """
        Parse a document and return structured text data with metadata:
        filename, total_pages, extracted_clause_count, parsing_status.
        """
        file_type = DocumentParser.detect_file_type(filename)
        
        try:
            if file_type == ".pdf":
                try:
                    result = DocumentParser._parse_pdf(file_path)
                except Exception as pdf_err:
                    logger.warning(f"PyMuPDF failed ({pdf_err}), attempting direct text fallback...")
                    result = DocumentParser._parse_txt(file_path)
            elif file_type in (".docx", ".doc"):
                try:
                    result = DocumentParser._parse_docx(file_path)
                except Exception as docx_err:
                    logger.warning(f"python-docx failed ({docx_err}), attempting XML fallback...")
                    result = DocumentParser._parse_docx_fallback(file_path)
            else:
                result = DocumentParser._parse_txt(file_path)

            # Segment clauses to compute extracted_clause_count immediately
            segmented = DocumentParser.segment_into_clauses(result["raw_text"], result["pages"])
            
            result["filename"] = filename
            result["total_pages"] = result["page_count"]
            result["extracted_clause_count"] = len(segmented)
            result["clauses"] = segmented
            result["parsing_status"] = "NLP Pipeline Ingestion Ready"
            
            return result

        except Exception as e:
            logger.error(f"Failed to parse document {filename}: {e}")
            raise RuntimeError(f"Could not parse document: {str(e)}")

    @staticmethod
    def _parse_pdf(file_path: str) -> Dict[str, Any]:
        """Parse PDF using PyMuPDF (pymupdf / fitz)."""
        try:
            import pymupdf
            doc = pymupdf.open(file_path)
        except ImportError:
            try:
                import fitz
                doc = fitz.open(file_path)
            except ImportError:
                raise ImportError("PyMuPDF not installed. Run: pip install pymupdf")

        pages = []
        full_text_parts = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            text = DocumentParser._clean_text(text)
            pages.append({"page_number": page_num + 1, "text": text})
            if text:
                full_text_parts.append(text)

        total_pages = max(1, len(doc))
        doc.close()
        raw_text = "\n\n".join(full_text_parts) if full_text_parts else "Empty document content."

        return {
            "raw_text": raw_text,
            "page_count": total_pages,
            "pages": pages,
            "file_type": "pdf",
        }

    @staticmethod
    def _parse_docx(file_path: str) -> Dict[str, Any]:
        """Parse DOCX using python-docx."""
        try:
            import docx
            doc = docx.Document(file_path)
            
            paragraphs = []
            pages = []
            current_page_text = []
            page_num = 1
            char_count = 0

            for p in doc.paragraphs:
                p_text = p.text.strip()
                if not p_text:
                    continue
                paragraphs.append(p_text)
                current_page_text.append(p_text)
                char_count += len(p_text)
                
                # Approximate 2500 chars per standard contract page
                if char_count > 2500:
                    pages.append({"page_number": page_num, "text": "\n\n".join(current_page_text)})
                    page_num += 1
                    current_page_text = []
                    char_count = 0

            if current_page_text:
                pages.append({"page_number": page_num, "text": "\n\n".join(current_page_text)})

            if not pages:
                pages = [{"page_number": 1, "text": ""}]

            raw_text = "\n\n".join(paragraphs)
            raw_text = DocumentParser._clean_text(raw_text)

            return {
                "raw_text": raw_text,
                "page_count": max(1, len(pages)),
                "pages": pages,
                "file_type": "docx",
            }
        except Exception:
            return DocumentParser._parse_docx_fallback(file_path)

    @staticmethod
    def _parse_docx_fallback(file_path: str) -> Dict[str, Any]:
        """Native fallback using zipfile and xml without external dependencies."""
        import zipfile
        import xml.etree.ElementTree as ET
        paragraphs = []
        try:
            with zipfile.ZipFile(file_path) as docx_zip:
                xml_content = docx_zip.read('word/document.xml')
                tree = ET.fromstring(xml_content)
                ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
                for p in tree.iterfind('.//w:p', ns):
                    texts = [node.text for node in p.iterfind('.//w:t', ns) if node.text]
                    if texts:
                        paragraphs.append(''.join(texts))
                raw_text = "\n\n".join(paragraphs)
        except Exception:
            with open(file_path, 'rb') as f:
                content = f.read()
                raw_text = re.sub(r'[^\x20-\x7E\n\t]', ' ', content.decode('utf-8', errors='ignore'))

        raw_text = DocumentParser._clean_text(raw_text)
        estimated_pages = max(1, len(raw_text) // 2500)
        pages = [{"page_number": 1, "text": raw_text}]

        return {
            "raw_text": raw_text,
            "page_count": estimated_pages,
            "pages": pages,
            "file_type": "docx",
        }

    @staticmethod
    def _parse_txt(file_path: str) -> Dict[str, Any]:
        """Read plain text document directly."""
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            raw_text = f.read()
        raw_text = DocumentParser._clean_text(raw_text)
        estimated_pages = max(1, len(raw_text) // 2500)
        return {
            "raw_text": raw_text,
            "page_count": estimated_pages,
            "pages": [{"page_number": 1, "text": raw_text}],
            "file_type": "txt",
        }

    @staticmethod
    def _clean_text(text: str) -> str:
        """Remove control characters, normalize whitespace, preserve paragraph structure."""
        if not text:
            return ""
        # Remove null bytes and non-printable control chars
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
        # Collapse excessive inline spaces and tabs
        text = re.sub(r"[ \t]+", " ", text)
        # Normalize multiple newlines to clean paragraph breaks
        text = re.sub(r"\n{3,}", "\n\n", text)
        # Remove standalone page numbers (e.g. line with just "1" or "- 2 -")
        text = re.sub(r"^\s*[-—]?\s*\d+\s*[-—]?\s*$", "", text, flags=re.MULTILINE)
        return text.strip()

    @staticmethod
    def segment_into_clauses(raw_text: str, pages: List[Dict]) -> List[Dict[str, Any]]:
        """
        Segment document text into individual legal clauses while preserving:
        - Exact page numbers
        - Section headers
        - Paragraph boundaries
        - Character offsets
        """
        if not raw_text or not raw_text.strip():
            return []

        # Build a character-offset to page number index
        char_page_map = []
        for p in pages:
            page_text = p.get("text", "")
            page_num = p.get("page_number", 1)
            char_page_map.extend([page_num] * (len(page_text) + 2))

        # Regex patterns for contract section headers:
        # 1. Numbered clauses: "1.", "1.1", "SECTION 1", "Article 1", "Clause 2"
        # 2. Uppercase Section Headers followed by newline: "PAYMENT TERMS & FEES"
        clause_patterns = [
            r"(?=(?:^|\n)(?:SECTION|Article|Clause|Schedule|Exhibit)\s+\d+[\.:\s])",
            r"(?=(?:^|\n)\d+\.\s+[A-Z])",
            r"(?=(?:^|\n)[A-Z0-9\s,\-\&]{4,60}:\s*\n)",
        ]

        combined_pattern = "|".join(clause_patterns)
        splits = re.split(combined_pattern, raw_text, flags=re.MULTILINE | re.IGNORECASE)

        clauses = []
        start_char = 0

        for part in splits:
            if not part:
                continue
            cleaned = part.strip()
            # Retain any meaningful contractual sentence or paragraph
            if len(cleaned) < 25:
                start_char += len(part)
                continue

            end_char = start_char + len(part)
            # Find exact page provenance
            p_idx = min(start_char, len(char_page_map) - 1) if char_page_map else 0
            page_num = char_page_map[p_idx] if char_page_map else 1

            clause_num = len(clauses) + 1
            clauses.append({
                "id": f"CLAUSE-{clause_num:03d}",
                "index": len(clauses),
                "raw_text": cleaned,
                "cleaned_text": DocumentParser._clean_text(cleaned),
                "page_number": page_num,
                "start_char": start_char,
                "end_char": end_char,
            })
            start_char = end_char

        # Fallback to double newline paragraphs if regex didn't split well
        if len(clauses) <= 1:
            paragraphs = [p.strip() for p in raw_text.split("\n\n") if len(p.strip()) >= 25]
            if len(paragraphs) > 1:
                clauses = []
                cur_char = 0
                for i, para in enumerate(paragraphs):
                    p_idx = min(cur_char, len(char_page_map) - 1) if char_page_map else 0
                    page_num = char_page_map[p_idx] if char_page_map else 1
                    clause_num = i + 1
                    clauses.append({
                        "id": f"CLAUSE-{clause_num:03d}",
                        "index": i,
                        "raw_text": para,
                        "cleaned_text": DocumentParser._clean_text(para),
                        "page_number": page_num,
                        "start_char": cur_char,
                        "end_char": cur_char + len(para),
                    })
                    cur_char += len(para) + 2

        logger.info(f"DocumentParser successfully segmented {len(clauses)} clauses across {len(pages)} pages.")
        return clauses
