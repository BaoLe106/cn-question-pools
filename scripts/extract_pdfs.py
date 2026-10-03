from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT.parent
OUTPUT_DIR = ROOT / "extracted"


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    summary = []
    for module_number in range(1, 7):
        pdf_path = SOURCE_DIR / f"Module {module_number} Question Pool.pdf"
        result = subprocess.run(
            ["pdftotext", "-layout", str(pdf_path), "-"],
            check=True,
            capture_output=True,
            text=True,
        )
        text = result.stdout.replace("\f", "\n\n--- PAGE BREAK ---\n\n").strip()
        output_path = OUTPUT_DIR / f"module-{module_number}.txt"
        output_path.write_text(text, encoding="utf-8")
        summary.append(
            {
                "module": module_number,
                "pages": text.count("--- PAGE BREAK ---") + 1,
                "characters": len(text),
                "output": str(output_path),
            }
        )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
