"""
Icon Management Module for OASIS Infobyte Weather Application.
Downloads and caches OpenWeatherMap weather icons via Pillow (PIL).
Provides crisp procedural vector-style fallbacks when offline or loading fails.
Uses Python standard library (urllib.request) for zero extra network dependencies.
"""

import io
import os
import urllib.request
import urllib.error

# Gracefully handle optional PIL and ImageTk dependencies
try:
    from PIL import Image, ImageDraw, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    Image = None
    ImageDraw = None
    ImageTk = None

from config import ICON_URL_TEMPLATE


# Directory to cache downloaded icons
ICONS_DIR = os.path.join(os.path.dirname(__file__), "assets", "icons")
os.makedirs(ICONS_DIR, exist_ok=True)

# In-memory PhotoImage cache to prevent garbage collection
_photo_image_cache: dict[str, object] = {}
_pil_image_cache: dict[str, object] = {}


def _download_icon_bytes(icon_code: str) -> bytes | None:
    """Downloads icon bytes using standard library urllib."""
    url = ICON_URL_TEMPLATE.format(icon=icon_code)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "WeatherApp/2.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status == 200:
                return resp.read()
    except Exception:
        pass
    return None


def _draw_procedural_icon(icon_code: str, size: tuple[int, int]):
    """Generates a high-quality fallback PIL weather icon when offline."""
    if not HAS_PIL or Image is None or ImageDraw is None:
        return None

    img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    prefix = icon_code[:2] if len(icon_code) >= 2 else "01"
    is_night = icon_code.endswith("n")

    if prefix == "01":  # Clear sky (Sun or Moon)
        if is_night:
            # Crescent Moon
            draw.ellipse([34, 24, 94, 84], fill="#cbd5e1")
            draw.ellipse([48, 18, 102, 78], fill=(0, 0, 0, 0))
        else:
            # Vibrant Sun
            draw.ellipse([34, 34, 94, 94], fill="#f59e0b", outline="#fbbf24", width=3)
            # Rays
            for offset in [(64, 10, 64, 24), (64, 104, 64, 118), (10, 64, 24, 64), (104, 64, 118, 64)]:
                draw.line(offset, fill="#fbbf24", width=4)

    elif prefix in ("02", "03", "04"):  # Clouds
        if prefix == "02" and not is_night:
            # Sun peeking
            draw.ellipse([54, 24, 94, 64], fill="#f59e0b")
        # Soft cloud puffs
        draw.ellipse([24, 52, 64, 92], fill="#94a3b8")
        draw.ellipse([48, 38, 92, 82], fill="#cbd5e1")
        draw.ellipse([70, 52, 108, 90], fill="#94a3b8")
        draw.rectangle([40, 64, 94, 92], fill="#cbd5e1")

    elif prefix in ("09", "10"):  # Rain / Shower Rain
        # Cloud
        draw.ellipse([24, 36, 64, 76], fill="#64748b")
        draw.ellipse([48, 22, 92, 66], fill="#94a3b8")
        draw.ellipse([70, 36, 108, 74], fill="#64748b")
        draw.rectangle([40, 48, 94, 76], fill="#94a3b8")
        # Raindrops
        for x in (40, 58, 76, 92):
            draw.line([(x, 86), (x - 6, 108)], fill="#38bdf8", width=3)

    elif prefix == "11":  # Thunderstorm
        # Dark storm cloud
        draw.ellipse([24, 30, 64, 70], fill="#334155")
        draw.ellipse([48, 16, 92, 60], fill="#475569")
        draw.ellipse([70, 30, 108, 68], fill="#334155")
        draw.rectangle([40, 42, 94, 70], fill="#475569")
        # Lightning bolt
        draw.polygon([(68, 72), (54, 92), (64, 92), (52, 114), (74, 88), (64, 88)], fill="#facc15")

    elif prefix == "13":  # Snow
        # Cloud
        draw.ellipse([24, 36, 64, 76], fill="#64748b")
        draw.ellipse([48, 22, 92, 66], fill="#94a3b8")
        draw.ellipse([70, 36, 108, 74], fill="#64748b")
        # Snow dots
        for x, y in [(42, 90), (64, 98), (86, 90), (52, 110), (74, 110)]:
            draw.ellipse([x - 4, y - 4, x + 4, y + 4], fill="#e0f2fe")

    elif prefix == "50":  # Mist / Fog
        for y in (36, 52, 68, 84, 100):
            draw.line([(24, y), (104, y)], fill="#94a3b8", width=4)

    else:
        # Generic globe / marker
        draw.ellipse([34, 34, 94, 94], fill="#38bdf8", outline="#e0f2fe", width=2)

    return img.resize(size, Image.Resampling.LANCZOS)


def get_weather_photo_image(icon_code: str, size: tuple[int, int] = (64, 64)):
    """
    Returns an ImageTk.PhotoImage for the specified OpenWeatherMap icon code.
    Attempts local disk cache -> remote OpenWeatherMap download -> procedural fallback.
    Caches the result in memory.
    Returns None if Pillow or Tkinter is not available.
    """
    if not HAS_PIL or Image is None or ImageTk is None:
        return None

    cache_key = f"{icon_code}_{size[0]}x{size[1]}"
    if cache_key in _photo_image_cache:
        return _photo_image_cache[cache_key]

    pil_img = None
    local_path = os.path.join(ICONS_DIR, f"{icon_code}.png")

    # 1. Try local disk cache
    if os.path.exists(local_path):
        try:
            pil_img = Image.open(local_path).convert("RGBA")
        except Exception:
            pil_img = None

    # 2. Try remote download via standard library urllib
    if pil_img is None:
        raw_bytes = _download_icon_bytes(icon_code)
        if raw_bytes:
            try:
                pil_img = Image.open(io.BytesIO(raw_bytes)).convert("RGBA")
                try:
                    pil_img.save(local_path, "PNG")
                except Exception:
                    pass
            except Exception:
                pil_img = None

    # 3. Use procedural PIL vector fallback
    if pil_img is None:
        pil_img = _draw_procedural_icon(icon_code, size)
    else:
        pil_img = pil_img.resize(size, Image.Resampling.LANCZOS)

    if pil_img is None:
        return None

    # Convert to Tkinter PhotoImage
    try:
        photo = ImageTk.PhotoImage(pil_img)
        _photo_image_cache[cache_key] = photo
        _pil_image_cache[cache_key] = pil_img
        return photo
    except Exception:
        return None
