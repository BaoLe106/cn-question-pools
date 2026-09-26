from __future__ import annotations

import json
import re
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT.parent
OUTPUT_DIR = ROOT / "extracted"


def clean_text(text: str) -> str:
    text = text.replace("\u00a0", " ").replace("\r\n", "\n")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    summary = []
    for module_number in range(1, 4):
        pdf_path = SOURCE_DIR / f"Module {module_number} Question Pool.pdf"
        reader = PdfReader(pdf_path)
        pages = [clean_text(page.extract_text() or "") for page in reader.pages]
        text = "\n\n--- PAGE BREAK ---\n\n".join(pages)
        output_path = OUTPUT_DIR / f"module-{module_number}.txt"
        output_path.write_text(text, encoding="utf-8")
        summary.append(
            {
                "module": module_number,
                "pages": len(pages),
                "characters": len(text),
                "output": str(output_path),
            }
        )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
