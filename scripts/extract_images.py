from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT.parent
OUTPUT_DIR = ROOT / "assets" / "images"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    catalog: list[dict[str, object]] = []
    seen: dict[str, str] = {}

    for module_number in range(1, 7):
        pdf_path = SOURCE_DIR / f"Module {module_number} Question Pool.pdf"
        listing = subprocess.run(
            ["pdfimages", "-list", str(pdf_path)],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()[2:]
        with tempfile.TemporaryDirectory() as temp_dir:
            prefix = Path(temp_dir) / "figure"
            subprocess.run(["pdfimages", "-all", str(pdf_path), str(prefix)], check=True)
            for line in listing:
                fields = line.split()
                if len(fields) < 7 or fields[2] != "image":
                    continue
                page_number, image_index = int(fields[0]), int(fields[1])
                width, height = int(fields[3]), int(fields[4])
                source = next(Path(temp_dir).glob(f"figure-{image_index:03d}.*"))
                content = source.read_bytes()
                digest = hashlib.sha256(content).hexdigest()[:12]
                filename = seen.get(digest)
                if filename is None:
                    filename = f"figure-{digest}{source.suffix}"
                    destination = OUTPUT_DIR / filename
                    if not destination.exists():
                        shutil.copyfile(source, destination)
                    seen[digest] = filename
                catalog.append(
                    {
                        "module": module_number,
                        "page": page_number,
                        "index": image_index,
                        "file": filename,
                        "width": width,
                        "height": height,
                    }
                )

    (OUTPUT_DIR / "catalog.json").write_text(
        json.dumps(catalog, indent=2), encoding="utf-8"
    )
    print(f"Extracted {len(seen)} unique figures from {len(catalog)} placements.")
    print(json.dumps(catalog, indent=2))


if __name__ == "__main__":
    main()
