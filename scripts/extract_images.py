from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pymupdf


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT.parent
OUTPUT_DIR = ROOT / "assets" / "images"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    catalog: list[dict[str, object]] = []
    seen: dict[str, str] = {}

    for module_number in range(1, 4):
        document = pymupdf.open(SOURCE_DIR / f"Module {module_number} Question Pool.pdf")
        for page_number, page in enumerate(document, start=1):
            for image_index, image_info in enumerate(page.get_images(full=True), start=1):
                xref = image_info[0]
                image = document.extract_image(xref)
                digest = hashlib.sha256(image["image"]).hexdigest()[:12]
                filename = seen.get(digest)
                if filename is None:
                    filename = f"figure-{digest}.{image['ext']}"
                    (OUTPUT_DIR / filename).write_bytes(image["image"])
                    seen[digest] = filename
                catalog.append(
                    {
                        "module": module_number,
                        "page": page_number,
                        "index": image_index,
                        "file": filename,
                        "width": image["width"],
                        "height": image["height"],
                    }
                )

    (OUTPUT_DIR / "catalog.json").write_text(
        json.dumps(catalog, indent=2), encoding="utf-8"
    )
    print(f"Extracted {len(seen)} unique figures from {len(catalog)} placements.")
    print(json.dumps(catalog, indent=2))


if __name__ == "__main__":
    main()
