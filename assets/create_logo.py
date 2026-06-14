from PIL import Image, ImageDraw
import os

SIZE = 512
BG = (0, 0, 0, 255)
BLUE = (65, 145, 200, 255)

img = Image.new("RGBA", (SIZE, SIZE), BG)
draw = ImageDraw.Draw(img)

cx, cy = SIZE // 2, SIZE // 2
radius = 180
outline_width = 28

draw.ellipse(
    [cx - radius, cy - radius, cx + radius, cy + radius],
    outline=BLUE,
    width=outline_width,
)

arrow_head_height = 130
arrow_head_half_width = 95
shaft_half_width = 30
shaft_top = cy - arrow_head_height // 3
shaft_bottom = cy + 100
head_top = cy - arrow_head_height + 20

draw.polygon([
    (cx, head_top),
    (cx - arrow_head_half_width, shaft_top),
    (cx + arrow_head_half_width, shaft_top),
], fill=BLUE)

draw.rectangle(
    [cx - shaft_half_width, shaft_top - 10, cx + shaft_half_width, shaft_bottom],
    fill=BLUE,
)

out_dir = os.path.dirname(os.path.abspath(__file__))

png_path = os.path.join(out_dir, "logo.png")
img.save(png_path, "PNG")
print(f"Saved: {png_path}")

# Create ICO with proper sizes for Windows (including 32x32 for taskbar)
sizes_ico = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
ico_images = []
for s in sizes_ico:
    ico_images.append(img.resize(s, Image.Resampling.LANCZOS))

ico_path = os.path.join(out_dir, "icon.ico")
ico_images[0].save(ico_path, format="ICO", sizes=sizes_ico, append_images=ico_images[1:])
print(f"Saved: {ico_path}")
