from pathlib import Path

import fitz


root = Path(__file__).resolve().parents[1]
source = root.parent

for module_number in range(1, 4):
    path = source / f"Module {module_number} Question Pool.pdf"
    document = fitz.open(path)
    print(f"MODULE {module_number}: {len(document)} pages")
    for page_number, page in enumerate(document, start=1):
        images = page.get_images(full=True)
        if images:
            dimensions = [f"{item[2]}x{item[3]}" for item in images]
            text = page.get_text("text").replace("\n", " ")[:100]
            print(f"  page {page_number}: {len(images)} image(s) {dimensions} | {text}")
