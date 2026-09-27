#!/usr/bin/env python3
"""Kinetic typography reel generator — recreates the reference video's text animation.
Usage: python3 reel.py preview | render
"""
import os, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1280, 720, 30
MAROON = (91, 32, 54)
YELLOW = (245, 197, 16)
WHITE = (253, 245, 250)
INK = (35, 8, 18)

SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"

# ---------------- helpers ----------------
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))

def ease_out_cubic(p):
    p = clamp(p)
    return 1 - (1 - p) ** 3

def ease_out_back(p):
    p = clamp(p)
    c = 1.70158
    return 1 + (c + 1) * ((p - 1) ** 3) + c * ((p - 1) ** 2)

def prog(t, t0, dur):
    return clamp((t - t0) / dur)

_font_cache = {}
def font(path, size):
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]

def layout_line(text, fnt, tracking=0):
    xs, adv = [], []
    x = 0.0
    for i, ch in enumerate(text):
        try:
            w = fnt.getlength(ch)
        except Exception:
            bb = fnt.getbbox(ch)
            w = bb[2] - bb[0]
        xs.append(x)
        adv.append(w)
        x += w + (tracking if i < len(text) - 1 else 0)
    asc, desc = fnt.getmetrics()
    return xs, adv, x, asc, desc

def render_line(text, path, size, fill, stroke_w=0, stroke_fill=None, tracking=0):
    """Render a full line to a tight RGBA layer. Returns dict with layer + char geometry."""
    fnt = font(path, size)
    xs, adv, total, asc, desc = layout_line(text, fnt, tracking)
    pad = stroke_w + 4
    lw, lh = int(math.ceil(total)) + pad * 2, asc + desc + pad * 2
    layer = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for ch, cx in zip(text, xs):
        if ch == " ":
            continue
        d.text((pad + cx, pad + asc), ch, font=fnt, fill=fill,
               anchor="ls", stroke_width=stroke_w, stroke_fill=stroke_fill or fill)
    words = []
    for w in text.split(" "):
        pass
    # word ranges (char indices) for word-level animation
    ranges, i = [], 0
    for w in text.split(" "):
        if w:
            ranges.append((i, i + len(w)))
        i += len(w) + 1
    return {"layer": layer, "xs": xs, "adv": adv, "pad": pad, "w": lw, "h": lh,
            "ranges": ranges, "text": text}

def shear_italic(img, s=0.20):
    w, h = img.size
    shift = int(s * h)
    canvas = Image.new("RGBA", (w + shift + 4, h), (0, 0, 0, 0))
    canvas.paste(img, (2, 0), img)
    # output(x) samples input(x + s*y - s*h): top shifts right -> italic /
    return canvas.transform(canvas.size, Image.AFFINE, (1, s, -s * h + 2, 0, 1, 0),
                            resample=Image.BICUBIC)

def faded(img, a):
    if a >= 0.999:
        return img
    if a <= 0.001:
        return None
    im = img.copy()
    al = im.getchannel("A").point(lambda v: int(v * clamp(a)))
    im.putalpha(al)
    return im

def paste(base, img, cx, cy):
    """Paste img centered at (cx, cy)."""
    if img is None:
        return
    x = int(round(cx - img.size[0] / 2))
    y = int(round(cy - img.size[1] / 2))
    base.alpha_composite(img, (x, y))

def char_sprite(line, idx):
    """Cropped sprite of a single char (with stroke bleed)."""
    l = line["layer"]
    x0 = int(line["pad"] + line["xs"][idx]) - 3
    x1 = int(line["pad"] + line["xs"][idx] + line["adv"][idx]) + 3
    return l.crop((max(0, x0), 0, min(l.size[0], x1), l.size[1]))

def draw_typewriter(base, line, cx, cy, t, t0, per_char, char_dur=0.28, rise=26):
    n = len(line["text"])
    for i, ch in enumerate(line["text"]):
        if ch == " ":
            continue
        p = ease_out_cubic(prog(t, t0 + i * per_char, char_dur))
        if p <= 0:
            continue
        sp = char_sprite(line, i)
        sp = faded(sp, p)
        if sp is None:
            continue
        char_cx = cx - line["w"] / 2 + line["pad"] + line["xs"][i] + line["adv"][i] / 2
        paste(base, sp, char_cx, cy + (1 - p) * rise)

def draw_word_slides(base, words, cx, cy, t, t0, stagger=0.25, dur=0.35,
                     dx=120, dy=0):
    """words: list of (line_dict, t_offset). Slides each word in from (dx,dy)."""
    total_w = sum(w["w"] for w, _ in words)
    x = cx - total_w / 2
    for w, off in words:
        p = ease_out_cubic(prog(t, t0 + off * stagger, dur))
        if p > 0:
            spr = faded(w["layer"], p)
            paste(base, spr, x + w["w"] / 2 + (1 - p) * dx, cy + (1 - p) * dy)
        x += w["w"]

# ---------------- stickers ----------------
_sticker_cache = {}
def sticker(name, height):
    key = (name, height)
    if key in _sticker_cache:
        return _sticker_cache[key]
    src = f"assets/{name}.png"
    cut = f"assets/{name}_cut.png"
    if os.path.exists(cut):
        rgba = Image.open(cut).convert("RGBA")
    else:
        im = Image.open(src).convert("RGB")
        a = np.array(im).astype(np.int32)
        R, G, B = a[:, :, 0], a[:, :, 1], a[:, :, 2]
        green = (G > 120) & ((G - R) > 35) & ((G - B) > 35)
        alpha = np.where(green, 0, 255).astype(np.uint8)
        al = Image.fromarray(alpha).filter(ImageFilter.GaussianBlur(0.8))
        rgba = im.convert("RGBA")
        rgba.putalpha(al)
        rgba = rgba.crop(rgba.getbbox())
        rgba.save(cut)
    w = int(rgba.size[0] * height / rgba.size[1])
    out = rgba.resize((w, height), Image.LANCZOS)
    _sticker_cache[key] = out
    return out

# ---------------- walking cat ----------------
def cat_layer(phase, size=64):
    h = size
    w = int(size * 1.9)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    C = (12, 5, 10, 255)
    # tail (curve up at back)
    d.line([(14, h - 22), (6, h - 40), (12, h - 56)], fill=C, width=max(3, size // 16))
    # body
    d.ellipse([16, h - 44, w - 34, h - 16], fill=C)
    # head (front, facing right)
    hx0, hy0 = w - 46, 6
    d.ellipse([hx0, hy0, hx0 + 32, hy0 + 30], fill=C)
    # ears
    d.polygon([(hx0 + 4, hy0 + 6), (hx0 + 10, hy0 - 8), (hx0 + 16, hy0 + 4)], fill=C)
    d.polygon([(hx0 + 18, hy0 + 4), (hx0 + 26, hy0 - 6), (hx0 + 30, hy0 + 8)], fill=C)
    # legs (2-frame walk)
    off = [0, 5, 5, 0] if phase else [5, 0, 0, 5]
    for i, lx in enumerate([30, 48, 64, 80]):
        lx = int(lx / 100 * (w - 30)) + 8
        d.rectangle([lx, h - 18 - off[i], lx + 7, h - 4], fill=C)
    return img

def draw_cat(base, t_global):
    speed = 95  # px/s
    span = W + 240
    x = (t_global * speed) % span - 120
    bob = math.sin(t_global * 9) * 3
    phase = int(t_global * 6) % 2 == 0
    cat = cat_layer(phase)
    base.alpha_composite(cat, (int(x), int(H - 78 + bob)))

# ---------------- pre-rendered text ----------------
T = {}
def build_text():
    T["bhai"] = render_line("bhai", SANS, 120, WHITE)
    T["kuch"] = render_line("kuch ", SANS, 120, YELLOW, 3, INK)
    T["kamane"] = render_line("kamane", SANS, 120, YELLOW, 3, INK)
    T["kliye"] = render_line("ke liye", SANS, 62, WHITE)
    T["sub"] = render_line("ye do website batata hun", SANS, 54, WHITE)
    T["trust"] = render_line("bina kisi comment wali", SANS, 96, YELLOW, 3, INK)
    bk = render_line("bakwaas ke", SERIF, 78, WHITE)
    bk["layer"] = shear_italic(bk["layer"])
    T["bakwaas"] = bk
    pehli = render_line("PEHLI", SANS, 150, WHITE)
    pehli["layer"] = pehli["layer"].rotate(90, expand=True, resample=Image.BICUBIC)
    pehli["w"], pehli["h"] = pehli["layer"].size
    T["pehli"] = pehli
    T["ws1"] = render_line("website", SANS, 118, YELLOW, 3, INK)
    T["ka"] = render_line("ka", SANS, 110, WHITE)
    T["naam"] = render_line("naam", SANS, 110, WHITE)
    hai = render_line("hai", SANS, 64, WHITE)
    hai["layer"] = hai["layer"].rotate(-90, expand=True, resample=Image.BICUBIC)
    hai["w"], hai["h"] = hai["layer"].size
    T["hai"] = hai
    T["ws2"] = render_line("2. website", SANS, 128, YELLOW, 3, INK)
    kn = render_line("ka naam hai", SERIF, 66, WHITE)
    T["kn2"] = kn
    T["bridge"] = render_line("yaha per kaafi saare", SERIF, 86, WHITE)
    adf = render_line("and don't forget", SERIF, 82, WHITE)
    adf["layer"] = shear_italic(adf["layer"])
    T["adf"] = adf
    T["press"] = render_line("to press", SANS, 118, YELLOW, 3, INK)
    fol = render_line("follow", SERIF, 82, WHITE)
    fol["layer"] = shear_italic(fol["layer"])
    T["follow"] = fol

# ---------------- cards (t = local seconds) ----------------
def card_hook(t):
    base = Image.new("RGBA", (W, H), MAROON + (255,))
    words = [(T["bhai"], 0), (T["kuch"], 1), (T["kamane"], 2)]
    total_w = sum(w["w"] for w, _ in words)
    x = 640 - total_w / 2
    # bhai: fades in centered, then glides left into its group slot
    slot_cx = x + T["bhai"]["w"] / 2
    glide = ease_out_cubic(prog(t, 0.55, 0.35))
    a_bhai = ease_out_cubic(prog(t, 0.10, 0.40))
    if a_bhai > 0:
        cx = 640 + (slot_cx - 640) * glide
        paste(base, faded(T["bhai"]["layer"], a_bhai), cx, 300 + (1 - a_bhai) * 24)
    # kuch / kamane slide in from the right
    xx = x + T["bhai"]["w"]
    for w, off in words[1:]:
        p = ease_out_cubic(prog(t, 0.66 + (off - 1) * 0.28, 0.35))
        if p > 0:
            paste(base, faded(w["layer"], p), xx + w["w"] / 2 + (1 - p) * 150, 300)
        xx += w["w"]
    p = ease_out_cubic(prog(t, 1.40, 0.30))
    if p > 0:
        paste(base, faded(T["kliye"]["layer"], p), 640, 180 + (1 - p) * 24)
    if t > 1.70:
        draw_typewriter(base, T["sub"], 700, 445, t, 1.70, 0.055)
    # kitten rises + bobs
    pk = ease_out_back(prog(t, 1.00, 0.55))
    if pk > 0:
        kit = sticker("kitten", 290)
        bob = math.sin(t * 11) * 8 if t > 1.6 else 0
        sway = math.sin(t * 5.5) * 10 if t > 1.6 else 0
        paste(base, kit, 235 + sway, H - 60 - kit.size[1] / 2 + (1 - pk) * 320 + bob)
    return base

def card_trust(t):
    base = Image.new("RGBA", (W, H), MAROON + (255,))
    p = ease_out_cubic(prog(t, 0.0, 0.45))
    if p > 0:
        paste(base, faded(T["trust"]["layer"], p), 640 + (1 - p) * 260, 450)
    ph = ease_out_cubic(prog(t, 0.30, 0.55))
    if ph > 0:
        hero = sticker("hanging_hero", 330)
        swing = math.sin(t * 5.0) * 4 * max(0, 1 - t / 2.5)
        hero = hero.rotate(swing, resample=Image.BICUBIC, center=(hero.size[0] / 2, 0))
        top_y = -hero.size[1] + ph * (hero.size[1] + 8)
        base.alpha_composite(hero, (int(470 - hero.size[0] / 2), int(top_y)))
    pb = ease_out_cubic(prog(t, 0.80, 0.35))
    if pb > 0:
        paste(base, faded(T["bakwaas"]["layer"], pb), 850 + (1 - pb) * 160, 565)
    return base

def card_pehli(t):
    base = Image.new("RGBA", (W, H), MAROON + (255,))
    p1 = ease_out_cubic(prog(t, 0.0, 0.45))
    if p1 > 0:
        paste(base, faded(T["pehli"]["layer"], p1), 330 + (1 - p1) * -160, 360)
    p2 = ease_out_back(prog(t, 0.30, 0.45))
    if p2 > 0:
        ws = T["ws1"]["layer"]
        s = 0.55 + 0.45 * min(p2, 1.15)
        w2 = ws.resize((int(ws.size[0] * s), int(ws.size[1] * s)), Image.LANCZOS)
        paste(base, faded(w2, clamp(p2 * 1.4)), 770, 360)
    p3 = ease_out_cubic(prog(t, 0.55, 0.4))
    if p3 > 0:
        paste(base, faded(T["ka"]["layer"], p3), 690, 205 + (1 - p3) * -120)
    p4 = ease_out_cubic(prog(t, 0.75, 0.4))
    if p4 > 0:
        paste(base, faded(T["naam"]["layer"], p4), 700, 515 + (1 - p4) * 120)
    p5 = ease_out_cubic(prog(t, 0.95, 0.35))
    if p5 > 0:
        paste(base, faded(T["hai"]["layer"], p5), 1005, 225)
    return base

def card_dusri(t):
    base = Image.new("RGBA", (W, H), MAROON + (255,))
    p = ease_out_cubic(prog(t, 0.0, 0.45))
    if p > 0:
        paste(base, faded(T["ws2"]["layer"], p), 640 + (1 - p) * 200, 400)
    pb = ease_out_cubic(prog(t, 0.20, 0.55))
    if pb > 0:
        boy = sticker("laughing_boy", 330)
        top_y = -boy.size[1] + pb * (boy.size[1] + 45)
        base.alpha_composite(boy, (int(790 - boy.size[0] / 2), int(top_y)))
    if t > 0.70:
        draw_typewriter(base, T["kn2"], 640, 560, t, 0.70, 0.06)
    return base

def card_bridge(t):
    base = Image.new("RGBA", (W, H), MAROON + (255,))
    draw_typewriter(base, T["bridge"], 640, 360, t, 0.10, 0.055, char_dur=0.32, rise=34)
    return base

def card_outro(t):
    base = Image.new("RGBA", (W, H), MAROON + (255,))
    p1 = ease_out_cubic(prog(t, 0.10, 0.5))
    if p1 > 0:
        paste(base, faded(T["adf"]["layer"], p1), 640, 250 + (1 - p1) * 30)
    p2 = ease_out_cubic(prog(t, 0.70, 0.4))
    if p2 > 0:
        paste(base, faded(T["press"]["layer"], p2), 640 + (1 - p2) * 180, 395)
    p3 = ease_out_cubic(prog(t, 1.20, 0.4))
    if p3 > 0:
        paste(base, faded(T["follow"]["layer"], p3), 640, 535 + (1 - p3) * 40)
    return base

TIMELINE = [
    (card_hook, 3.4),
    (card_trust, 2.4),
    (card_pehli, 2.6),
    (card_dusri, 2.6),
    (card_bridge, 2.4),
    (card_outro, 3.6),
]
TOTAL = sum(d for _, d in TIMELINE)

def render_frame(t_global):
    acc = 0.0
    for fn, dur in TIMELINE:
        if t_global < acc + dur:
            frame = fn(t_global - acc)
            break
        acc += dur
    else:
        frame = card_outro(TIMELINE[-1][1])
    draw_cat(frame, t_global)
    # quick fade in / fade out
    if t_global < 0.2:
        a = t_global / 0.2
        black = Image.new("RGBA", (W, H), (0, 0, 0, int(255 * (1 - a))))
        frame = Image.alpha_composite(frame, black)
    if t_global > TOTAL - 0.3:
        a = (TOTAL - t_global) / 0.3
        black = Image.new("RGBA", (W, H), (0, 0, 0, int(255 * (1 - a))))
        frame = Image.alpha_composite(frame, black)
    return frame.convert("RGB")

def preview():
    build_text()
    stamps = [1.2, 2.9, 4.6, 9.8, 12.4, 15.8]
    thumbs = []
    for ts in stamps:
        f = render_frame(ts).resize((640, 360), Image.LANCZOS)
        d = ImageDraw.Draw(f)
        d.text((12, 12), f"{ts:.1f}s", fill=(0, 255, 0))
        thumbs.append(f)
    grid = Image.new("RGB", (1280, 1080), (0, 0, 0))
    for i, th in enumerate(thumbs):
        grid.paste(th, ((i % 2) * 640, (i // 2) * 360))
    grid.save("preview_cards.png")
    print("saved preview_cards.png")

def render():
    import av
    build_text()
    os.makedirs("output", exist_ok=True)
    out = av.open("output/typography_reel.mp4", "w")
    stream = out.add_stream("libx264", rate=FPS)
    stream.width, stream.height = W, H
    stream.pix_fmt = "yuv420p"
    stream.options = {"preset": "medium", "crf": "18"}
    n = int(TOTAL * FPS)
    for i in range(n):
        t = i / FPS
        arr = np.array(render_frame(t))
        out.mux(stream.encode(av.VideoFrame.from_ndarray(arr, format="rgb24")))
        if i % 60 == 0:
            print(f"frame {i}/{n} ({t:.1f}s)", flush=True)
    out.mux(stream.encode())
    out.close()
    print("saved output/typography_reel.mp4")

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "preview"
    (render if mode == "render" else preview)()
