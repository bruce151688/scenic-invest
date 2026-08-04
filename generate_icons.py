"""生成 PWA 图标"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, output_path):
    """创建一个渐变背景+emoji的图标"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 渐变背景（模拟）
    for i in range(size):
        r = int(25 + (i / size) * 0)  # 蓝色
        g = int(137 + (i / size) * (7 - 137))  # 蓝到绿
        b = int(250 + (i / size) * (193 - 250))
        a = 255
        draw.rectangle([(0, i), (size, i + 1)], fill=(r, g, b, a))

    # 圆角矩形遮罩
    mask = Image.new('L', (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    radius = size // 5
    mask_draw.rounded_rectangle([(0, 0), (size - 1, size - 1)], radius=radius, fill=255)

    # 绘制文字
    try:
        # 尝试使用大字体
        font_size = size // 3
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()

    text = "🏔️"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text(((size - tw) // 2, (size - th) // 2 - size // 8), text, font=font, embedded_color=True)

    # 应用圆角遮罩
    img.putalpha(mask)
    img.save(output_path, "PNG")
    print(f"Created: {output_path} ({size}x{size})")

icons_dir = "frontend/public/icons"
os.makedirs(icons_dir, exist_ok=True)

create_icon(192, os.path.join(icons_dir, "icon-192.png"))
create_icon(512, os.path.join(icons_dir, "icon-512.png"))
print("Icons generated successfully!")
