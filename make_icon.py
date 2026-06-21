"""產生 App 圖示(純 Pillow)。輸出 apple-touch-icon / icon-192 / icon-512 / favicon。"""
from PIL import Image, ImageDraw, ImageFilter

S = 1024  # 高解析度母版,最後再縮

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def rounded_mask(size, radius):
    m = Image.new('L', (size, size), 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=255)
    return m

def make():
    img = Image.new('RGBA', (S, S), (0, 0, 0, 0))

    # --- 漸層底(上淺靛 → 下深藍) ---
    top = (58, 74, 140)     # #3a4a8c
    bot = (20, 28, 58)      # #141c3a
    grad = Image.new('RGB', (S, S), top)
    gd = ImageDraw.Draw(grad)
    for y in range(S):
        gd.line([(0, y), (S, y)], fill=lerp(top, bot, y / S))
    # 圓角遮罩
    img.paste(grad, (0, 0), rounded_mask(S, int(S * 0.225)))

    d = ImageDraw.Draw(img)
    cx = S / 2

    # --- 書本陰影(柔和) ---
    shadow = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.polygon([(180, 760), (S - 180, 760), (S - 150, 800), (150, 800)], fill=(0, 0, 0, 110))
    shadow = shadow.filter(ImageFilter.GaussianBlur(28))
    img = Image.alpha_composite(img, shadow)
    d = ImageDraw.Draw(img)

    # --- 翻開的書:左右兩頁 ---
    cream = (245, 240, 225)
    cream_dark = (225, 218, 198)
    # y 座標
    y_top_spine = 392      # 中央書脊頂(較低)
    y_top_edge = 352       # 外緣頂(較高 → 微微上揚)
    y_bot_spine = 712
    y_bot_edge = 700
    left_x = 198
    right_x = S - 198

    # 左頁(略深,當作底層)
    d.polygon([(cx, y_top_spine), (left_x, y_top_edge),
               (left_x, y_bot_edge), (cx, y_bot_spine)], fill=cream_dark)
    # 右頁(略深)
    d.polygon([(cx, y_top_spine), (right_x, y_top_edge),
               (right_x, y_bot_edge), (cx, y_bot_spine)], fill=cream_dark)
    # 上層頁面(亮一點,內縮做出層疊感)
    inset = 16
    d.polygon([(cx, y_top_spine + inset), (left_x + inset, y_top_edge + inset),
               (left_x + inset, y_bot_edge - inset), (cx, y_bot_spine - inset)], fill=cream)
    d.polygon([(cx, y_top_spine + inset), (right_x - inset, y_top_edge + inset),
               (right_x - inset, y_bot_edge - inset), (cx, y_bot_spine - inset)], fill=cream)

    # 書脊中線
    d.line([(cx, y_top_spine), (cx, y_bot_spine)], fill=(150, 140, 120), width=6)

    # --- 頁面文字線 ---
    line_col = (175, 168, 150)
    for i in range(5):
        ly = 452 + i * 50
        # 左頁文字線(隨頁面斜度內縮)
        d.line([(290, ly + 6), (cx - 40, ly)], fill=line_col, width=9)
        # 右頁文字線
        d.line([(cx + 40, ly), (S - 290, ly + 6)], fill=line_col, width=9)

    # --- 書籤緞帶(暖橘紅,從書頂垂下) ---
    rib = (232, 122, 70)     # #e87a46
    rib_dark = (205, 96, 50)
    rx = cx + 86            # 緞帶水平位置(偏右頁)
    rw = 46
    d.rectangle([rx - rw / 2, 318, rx + rw / 2, 560], fill=rib)
    # 緞帶底部 V 形缺口
    d.polygon([(rx - rw / 2, 560), (rx + rw / 2, 560), (rx, 522)], fill=(20, 28, 58, 0))
    # 用底色蓋出缺口(取漸層底對應區域近似:深藍)
    d.polygon([(rx - rw / 2, 562), (rx + rw / 2, 562), (rx, 524)], fill=lerp(top, bot, 0.52))
    # 緞帶側邊陰影
    d.rectangle([rx + rw / 2 - 8, 318, rx + rw / 2, 560], fill=rib_dark)

    return img.convert('RGBA')

master = make()

# 輸出各尺寸
outs = {
    'apple-touch-icon.png': 180,
    'icon-192.png': 192,
    'icon-512.png': 512,
    'favicon-48.png': 48,
}
for name, sz in outs.items():
    master.resize((sz, sz), Image.LANCZOS).save(name)
    print('wrote', name, sz)

# 預覽縮圖(拼一張看效果)
master.resize((256, 256), Image.LANCZOS).save('_preview_icon.png')
print('preview -> _preview_icon.png')
