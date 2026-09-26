from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


root = Path(__file__).resolve().parents[1]
image_dir = root / "assets" / "images"
files = sorted(path for path in image_dir.iterdir() if path.suffix.lower() in {".png", ".jpg", ".jpeg"})
tile_width, tile_height = 520, 330
sheet = Image.new("RGB", (tile_width * 3, tile_height * 5), "#f4f0e8")
draw = ImageDraw.Draw(sheet)
font = ImageFont.load_default(size=18)

for index, path in enumerate(files):
    image = Image.open(path).convert("RGB")
    image.thumbnail((tile_width - 30, tile_height - 55))
    x = (index % 3) * tile_width + (tile_width - image.width) // 2
    y = (index // 3) * tile_height + 35
    sheet.paste(image, (x, y))
    draw.text(((index % 3) * tile_width + 12, (index // 3) * tile_height + 10), path.name, fill="#18212a", font=font)

output = root / "contact-sheet.jpg"
sheet.save(output, quality=90)
print(output)
