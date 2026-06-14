from PIL import Image
import os

# Path to the source logo
logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
if not os.path.exists(logo_path):
    print(f"Error: {logo_path} not found.")
    exit(1)

sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
images = []

with Image.open(logo_path) as img:
    img = img.convert("RGBA")

    # Center-crop to square
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    img = img.crop((left, top, left + side, top + side))

    for size in sizes:
        resized_img = img.resize(size, Image.Resampling.LANCZOS)
        images.append(resized_img)

out_dir = os.path.dirname(os.path.abspath(__file__))
ico_path = os.path.join(out_dir, "icon.ico")
images[0].save(ico_path, format="ICO", sizes=sizes, append_images=images[1:])
print(f"New logo saved: {ico_path}")
