import io
import os
import math
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from PIL import Image, ImageDraw, ImageFont

from store.models import Category, Product
from banners.models import Banner

User = get_user_model()

# ==============================================================================
# CONFIGURABLE CONSTANTS (Modify as needed)
# ==============================================================================
TEST_USER_USERNAME = 'testuser'
TEST_USER_PASSWORD = 'TestUser123!'
TEST_USER_EMAIL = 'testuser@vcart.store'
TEST_USER_FIRST_NAME = 'Test'
TEST_USER_LAST_NAME = 'User'


# ==============================================================================
# FONT HELPER
# ==============================================================================

def get_font(size=20, bold=False):
    """
    Safely load a clean system font (Windows/Linux/macOS) or fallback to default.
    """
    font_candidates = [
        # Windows
        "C:\\Windows\\Fonts\\arialbd.ttf" if bold else "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\segoeuib.ttf" if bold else "C:\\Windows\\Fonts\\segoeui.ttf",
        "C:\\Windows\\Fonts\\calibrib.ttf" if bold else "C:\\Windows\\Fonts\\calibri.ttf",
        # Linux / container
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in font_candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


# ==============================================================================
# HIGH-FIDELITY VECTOR DRAWING ENGINE (Pure Pillow PNGs, Non-Copyrighted)
# ==============================================================================

def create_radial_gradient_canvas(width, height, inner_color, outer_color):
    """Create a canvas with smooth radial ambient studio lighting."""
    img = Image.new('RGBA', (width, height), outer_color)
    draw = ImageDraw.Draw(img)
    cx, cy = width // 2, height // 2
    max_radius = int(math.hypot(width, height) / 1.7)
    step = 4
    for r in range(max_radius, 0, -step):
        ratio = r / max_radius
        red = int(inner_color[0] + (outer_color[0] - inner_color[0]) * ratio)
        green = int(inner_color[1] + (outer_color[1] - inner_color[1]) * ratio)
        blue = int(inner_color[2] + (outer_color[2] - inner_color[2]) * ratio)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(red, green, blue, 255))
    return img


def draw_phone(draw, cx, cy, scale=1.0, is_pro=True, color_theme="titanium"):
    """
    Draw a precise, high-fidelity smartphone graphic.
    Features: Titanium/aluminum bezel, Dynamic Island, OLED wallpaper, Action button, Home bar.
    """
    w = int(220 * scale)
    h = int(450 * scale)
    r = int(38 * scale)
    x0, y0 = cx - w // 2, cy - h // 2
    x1, y1 = cx + w // 2, cy + h // 2

    chassis_colors = {
        "titanium": ((70, 75, 85), (35, 38, 45), (140, 145, 155)),
        "ultramarine": ((30, 60, 130), (15, 25, 60), (70, 130, 240)),
        "black": ((45, 45, 48), (20, 20, 22), (90, 90, 95)),
    }
    rim_outer, rim_inner, rim_highlight = chassis_colors.get(color_theme, chassis_colors["titanium"])

    # Outer Hardware Buttons
    btn_w = max(2, int(3 * scale))
    draw.rounded_rectangle([x0 - btn_w, y0 + int(70 * scale), x0, y0 + int(98 * scale)], radius=2, fill=rim_highlight)  # Action Button
    draw.rounded_rectangle([x0 - btn_w, y0 + int(115 * scale), x0, y0 + int(160 * scale)], radius=2, fill=rim_highlight)  # Vol Up
    draw.rounded_rectangle([x0 - btn_w, y0 + int(172 * scale), x0, y0 + int(217 * scale)], radius=2, fill=rim_highlight)  # Vol Down
    draw.rounded_rectangle([x1, y0 + int(120 * scale), x1 + btn_w, y0 + int(185 * scale)], radius=2, fill=rim_highlight)  # Power Button

    # Phone Outer Chassis
    draw.rounded_rectangle([x0, y0, x1, y1], radius=r, outline=rim_highlight, width=max(1, int(2 * scale)), fill=rim_outer)
    draw.rounded_rectangle([x0 + int(3 * scale), y0 + int(3 * scale), x1 - int(3 * scale), y1 - int(3 * scale)], radius=r - 2, fill=rim_inner)

    # Screen Bezel & Display
    bezel = int(8 * scale)
    sx0, sy0 = x0 + bezel, y0 + bezel
    sx1, sy1 = x1 - bezel, y1 - bezel
    draw.rounded_rectangle([sx0, sy0, sx1, sy1], radius=r - 6, fill=(5, 7, 12))

    # OLED Screen Wallpaper (Multi-color abstract aurora ribbons)
    sw = sx1 - sx0
    sh = sy1 - sy0
    for i in range(12):
        rad_x = int(sw * (0.8 - i * 0.05))
        rad_y = int(sh * (0.6 - i * 0.04))
        alpha_color = (
            int(15 + i * 14) if is_pro else int(10 + i * 8),
            int(45 + i * 16) if is_pro else int(70 + i * 15),
            int(180 - i * 10) if is_pro else int(230 - i * 12),
        )
        draw.ellipse([cx - rad_x // 2, cy - rad_y // 2, cx + rad_x // 2, cy + rad_y // 2], outline=alpha_color, width=max(1, int(2 * scale)))

    # Dynamic Island Pill
    pill_w = int(68 * scale)
    pill_h = int(20 * scale)
    draw.rounded_rectangle([cx - pill_w // 2, sy0 + int(12 * scale), cx + pill_w // 2, sy0 + int(12 * scale) + pill_h], radius=int(10 * scale), fill=(0, 0, 0))
    # Camera glint & sensor dot
    draw.ellipse([cx - int(18 * scale), sy0 + int(18 * scale), cx - int(10 * scale), sy0 + int(26 * scale)], fill=(12, 28, 64))
    draw.ellipse([cx + int(14 * scale), sy0 + int(19 * scale), cx + int(18 * scale), sy0 + int(23 * scale)], fill=(30, 30, 35))

    # Home Indicator Bar
    bar_w = int(80 * scale)
    draw.rounded_rectangle([cx - bar_w // 2, sy1 - int(14 * scale), cx + bar_w // 2, sy1 - int(10 * scale)], radius=2, fill=(200, 210, 225))


def draw_laptop(draw, cx, cy, scale=1.0, color_theme="space_black"):
    """
    Draw a precise, high-fidelity pro notebook computer.
    Features: Open Liquid Retina XDR display with camera notch, unibody aluminum deck, keyboard with spacebar, trackpad.
    """
    lw = int(420 * scale)
    lh = int(250 * scale)

    # 1. Open Screen Lid (Upper section)
    screen_w = int(360 * scale)
    screen_h = int(220 * scale)
    sx0, sy0 = cx - screen_w // 2, cy - int(95 * scale) - screen_h // 2
    sx1, sy1 = cx + screen_w // 2, cy - int(95 * scale) + screen_h // 2
    sr = int(14 * scale)

    # Lid Outer Metal Frame
    lid_rim = (120, 125, 135) if color_theme == "silver" else (55, 60, 70)
    lid_bg = (180, 185, 195) if color_theme == "silver" else (22, 24, 28)
    draw.rounded_rectangle([sx0, sy0, sx1, sy1], radius=sr, outline=lid_rim, width=max(1, int(2 * scale)), fill=lid_bg)

    # Display Bezel & Glass
    bezel = int(7 * scale)
    dsx0, dsy0 = sx0 + bezel, sy0 + bezel
    dsx1, dsy1 = sx1 - bezel, sy1 - bezel
    draw.rounded_rectangle([dsx0, dsy0, dsx1, dsy1], radius=sr - 4, fill=(4, 6, 10))

    # Display Wallpaper (High Dynamic Range creative curves)
    dw = dsx1 - dsx0
    dh = dsy1 - dsy0
    for i in range(14):
        offset = int(i * 12 * scale)
        color = (
            min(255, 10 + i * 16),
            min(255, 60 + i * 14),
            min(255, 200 - i * 8),
        )
        draw.arc([dsx0 + offset, dsy0 + int(30 * scale), dsx1 - offset, dsy1 + int(40 * scale)], start=180, end=360, fill=color, width=max(1, int(2 * scale)))

    # Display Notch & WebCam
    notch_w = int(34 * scale)
    notch_h = int(10 * scale)
    draw.rounded_rectangle([cx - notch_w // 2, dsy0, cx + notch_w // 2, dsy0 + notch_h], radius=2, fill=(4, 6, 10))
    draw.ellipse([cx - 2, dsy0 + 2, cx + 2, dsy0 + 6], fill=(40, 80, 140))

    # 2. Hinge Bar
    hw = int(140 * scale)
    draw.rounded_rectangle([cx - hw // 2, sy1 - 2, cx + hw // 2, sy1 + int(6 * scale)], radius=3, fill=(18, 20, 24))

    # 3. Base Keyboard Chassis (Perspective bottom deck)
    base_w = lw
    base_h = int(115 * scale)
    bx0, by0 = cx - base_w // 2, sy1 + 2
    bx1, by1 = cx + base_w // 2, by0 + base_h

    # Aluminum Base Deck
    deck_color = (200, 205, 215) if color_theme == "silver" else (30, 33, 38)
    deck_outline = (130, 135, 145) if color_theme == "silver" else (65, 70, 80)
    draw.rounded_rectangle([bx0, by0, bx1, by1], radius=int(10 * scale), outline=deck_outline, width=max(1, int(2 * scale)), fill=deck_color)

    # Chamfered Front Lip
    draw.line([bx0 + int(10 * scale), by1, bx1 - int(10 * scale), by1], fill=(90, 95, 105), width=max(1, int(2 * scale)))
    draw.rounded_rectangle([cx - int(40 * scale), by1 - int(4 * scale), cx + int(40 * scale), by1], radius=2, fill=(15, 16, 20))  # Display opening lip

    # Recessed Keyboard Well
    kw = int(340 * scale)
    kh = int(68 * scale)
    kx0, ky0 = cx - kw // 2, by0 + int(8 * scale)
    kx1, ky1 = cx + kw // 2, ky0 + kh
    draw.rounded_rectangle([kx0, ky0, kx1, ky1], radius=4, fill=(12, 13, 16))

    # Key Caps (Simulated chiclet layout)
    key_rows = 4
    key_cols = 12
    key_h = max(2, int((kh - 12) / key_rows))
    key_w = max(2, int((kw - 28) / key_cols))
    for r_idx in range(key_rows):
        cur_y = ky0 + 3 + r_idx * (key_h + 2)
        for c_idx in range(key_cols):
            cur_x = kx0 + 4 + c_idx * (key_w + 2)
            draw.rounded_rectangle([cur_x, cur_y, cur_x + key_w, cur_y + key_h], radius=1, fill=(28, 30, 35))

    # Spacebar
    sp_y = ky0 + 3 + (key_rows - 1) * (key_h + 2)
    draw.rounded_rectangle([cx - int(48 * scale), sp_y, cx + int(48 * scale), sp_y + key_h], radius=1, fill=(35, 38, 44))

    # Centered Force Touch Trackpad
    tw = int(110 * scale)
    th = int(32 * scale)
    tx0 = cx - tw // 2
    ty0 = ky1 + int(5 * scale)
    draw.rounded_rectangle([tx0, ty0, tx0 + tw, ty0 + th], radius=4, outline=(55, 60, 70), width=1, fill=(24, 26, 30))


def draw_earbuds(draw, cx, cy, scale=1.0):
    """
    Draw high-fidelity wireless earbuds and sleek magnetic charging case.
    """
    # 1. Charging Case (Left / Center-left)
    casew = int(160 * scale)
    caseh = int(120 * scale)
    case_x0 = cx - int(120 * scale)
    case_y0 = cy - caseh // 2
    case_x1 = case_x0 + casew
    case_y1 = case_y0 + caseh

    # Case Pebble Shell
    draw.rounded_rectangle([case_x0, case_y0, case_x1, case_y1], radius=int(36 * scale), outline=(220, 225, 235), width=max(1, int(2 * scale)), fill=(245, 248, 252))
    # Case Lid Seam Line
    seam_y = case_y0 + int(36 * scale)
    draw.line([case_x0 + 6, seam_y, case_x1 - 6, seam_y], fill=(180, 185, 195), width=max(1, int(2 * scale)))
    # LED Indicator Light (Glowing green)
    draw.ellipse([case_x0 + casew // 2 - 3, seam_y + int(24 * scale), case_x0 + casew // 2 + 3, seam_y + int(30 * scale)], fill=(52, 211, 153))

    # 2. Left and Right In-Ear Buds (Center-right)
    for idx, offset_x in enumerate([int(70 * scale), int(125 * scale)]):
        bud_x = cx + offset_x
        bud_y = cy - int(25 * scale)
        # Contoured acoustic head
        head_r = int(22 * scale)
        draw.ellipse([bud_x - head_r, bud_y - head_r, bud_x + head_r, bud_y + head_r], outline=(200, 205, 215), width=2, fill=(255, 255, 255))
        # Silicone In-Ear Tip
        tip_dir = -1 if idx == 0 else 1
        draw.ellipse([bud_x + tip_dir * int(14 * scale) - 10, bud_y - 10, bud_x + tip_dir * int(14 * scale) + 10, bud_y + 10], fill=(225, 230, 240))
        # Downward Stem
        stem_w = int(12 * scale)
        stem_h = int(60 * scale)
        draw.rounded_rectangle([bud_x - stem_w // 2, bud_y, bud_x + stem_w // 2, bud_y + stem_h], radius=4, outline=(200, 205, 215), width=1, fill=(250, 252, 255))
        # Chrome Charging Contacts at bottom
        draw.rounded_rectangle([bud_x - stem_w // 2 + 1, bud_y + stem_h - 4, bud_x + stem_w // 2 - 1, bud_y + stem_h], radius=1, fill=(160, 165, 175))
        # Mic Vent Indentation
        draw.line([bud_x - stem_w // 2 + 2, bud_y + int(20 * scale), bud_x + stem_w // 2 - 2, bud_y + int(20 * scale)], fill=(150, 155, 165), width=1)


def draw_headphones(draw, cx, cy, scale=1.0):
    """
    Draw luxury over-ear headphones with stainless steel mesh canopy and aluminum ear cups.
    """
    r = int(130 * scale)
    # Headband Mesh Canopy Arc
    draw.arc([cx - r, cy - r - int(50 * scale), cx + r, cy + r - int(50 * scale)], start=180, end=0, fill=(140, 145, 155), width=int(14 * scale))
    # Stainless Steel Telescoping Tubes
    draw.arc([cx - r + 4, cy - r - int(46 * scale), cx + r - 4, cy + r - int(46 * scale)], start=185, end=355, fill=(210, 215, 225), width=int(4 * scale))

    # Ear Cups (Left & Right)
    cup_w = int(58 * scale)
    cup_h = int(105 * scale)
    cup_r = int(24 * scale)

    for side in [-1, 1]:
        cup_cx = cx + side * r
        cup_cy = cy + int(10 * scale)
        x0, y0 = cup_cx - cup_w // 2, cup_cy - cup_h // 2
        x1, y1 = cup_cx + cup_w // 2, cup_cy + cup_h // 2

        # Outer Anodized Aluminum Shell
        draw.rounded_rectangle([x0, y0, x1, y1], radius=cup_r, outline=(180, 185, 195), width=max(1, int(2 * scale)), fill=(230, 235, 245))
        # Memory Foam Cushion Inset
        draw.rounded_rectangle([x0 + 6, y0 + 6, x1 - 6, y1 - 6], radius=cup_r - 4, outline=(140, 145, 155), width=1, fill=(195, 200, 210))

        # Digital Crown on Right Cup
        if side == 1:
            draw.rounded_rectangle([x1 - 2, y0 + int(12 * scale), x1 + int(6 * scale), y0 + int(26 * scale)], radius=2, fill=(160, 165, 175))


def draw_speaker(draw, cx, cy, scale=1.0):
    """
    Draw compact wireless smart speaker with 360-degree acoustic fabric mesh.
    """
    w = int(190 * scale)
    h = int(240 * scale)
    x0, y0 = cx - w // 2, cy - h // 2
    x1, y1 = cx + w // 2, cy + h // 2

    # Cylindrical Acoustic Fabric Body
    draw.rounded_rectangle([x0, y0, x1, y1], radius=int(60 * scale), outline=(45, 50, 60), width=max(1, int(2 * scale)), fill=(20, 23, 28))

    # Acoustic Mesh Texture Lines
    for y_step in range(y0 + 20, y1 - 20, int(10 * scale)):
        draw.line([x0 + int(12 * scale), y_step, x1 - int(12 * scale), y_step], fill=(32, 36, 44), width=1)

    # Top Circular Touch Panel
    panel_r = int(55 * scale)
    draw.ellipse([cx - panel_r, y0 - int(6 * scale), cx + panel_r, y0 + int(32 * scale)], outline=(60, 65, 75), width=2, fill=(10, 12, 16))

    # Glowing Assistant Ring & Volume Symbols
    glow_r = int(26 * scale)
    draw.ellipse([cx - glow_r, y0 + int(3 * scale), cx + glow_r, y0 + int(23 * scale)], outline=(56, 189, 248), width=2)
    # Plus & Minus icons
    draw.line([cx - int(32 * scale), y0 + int(13 * scale), cx - int(24 * scale), y0 + int(13 * scale)], fill=(180, 190, 205), width=2)  # -
    draw.line([cx + int(24 * scale), y0 + int(13 * scale), cx + int(32 * scale), y0 + int(13 * scale)], fill=(180, 190, 205), width=2)  # +
    draw.line([cx + int(28 * scale), y0 + int(9 * scale), cx + int(28 * scale), y0 + int(17 * scale)], fill=(180, 190, 205), width=2)


def draw_wireless_charger(draw, cx, cy, scale=1.0):
    """
    Draw dual magnetic fast-charging dock (MagSafe phone pad + Watch charging puck).
    """
    pad_w = int(320 * scale)
    pad_h = int(170 * scale)
    x0, y0 = cx - pad_w // 2, cy - pad_h // 2
    x1, y1 = cx + pad_w // 2, cy + pad_h // 2

    # Unibody Folding Base
    draw.rounded_rectangle([x0, y0, x1, y1], radius=int(28 * scale), outline=(70, 75, 85), width=max(1, int(2 * scale)), fill=(25, 28, 34))
    # Center Folding Hinge
    draw.line([cx, y0 + 6, cx, y1 - 6], fill=(45, 50, 60), width=max(1, int(3 * scale)))

    # Left: Magnetic Phone Charging Ring
    l_cx = cx - int(78 * scale)
    draw.ellipse([l_cx - 48, cy - 48, l_cx + 48, cy + 48], outline=(56, 189, 248), width=3, fill=(18, 20, 25))
    draw.ellipse([l_cx - 24, cy - 24, l_cx + 24, cy + 24], outline=(100, 116, 139), width=2)
    # Power Lightning Bolt
    bolt = [
        (l_cx + 3, cy - 14), (l_cx - 8, cy + 1), (l_cx, cy + 1),
        (l_cx - 3, cy + 14), (l_cx + 8, cy - 1), (l_cx, cy - 1)
    ]
    draw.polygon(bolt, fill=(250, 204, 21))

    # Right: Watch Pop-Up Charging Puck
    r_cx = cx + int(78 * scale)
    draw.ellipse([r_cx - 40, cy - 40, r_cx + 40, cy + 40], outline=(148, 163, 184), width=3, fill=(240, 243, 248))
    draw.ellipse([r_cx - 26, cy - 26, r_cx + 26, cy + 26], outline=(200, 205, 215), width=2, fill=(255, 255, 255))


def draw_leather_case(draw, cx, cy, scale=1.0):
    """
    Draw finely tanned European leather protective case with MagSafe magnetic ring.
    """
    w = int(220 * scale)
    h = int(450 * scale)
    r = int(38 * scale)
    x0, y0 = cx - w // 2, cy - h // 2
    x1, y1 = cx + w // 2, cy + h // 2

    # Rich Saddle Leather Back
    draw.rounded_rectangle([x0, y0, x1, y1], radius=r, outline=(160, 90, 45), width=max(1, int(2 * scale)), fill=(115, 62, 32))
    # Perimeter Stitched Contour
    draw.rounded_rectangle([x0 + 6, y0 + 6, x1 - 6, y1 - 6], radius=r - 4, outline=(140, 75, 38), width=1)

    # Top-Left Camera Cutout Ring
    cam_size = int(90 * scale)
    cx0, cy0 = x0 + int(16 * scale), y0 + int(16 * scale)
    draw.rounded_rectangle([cx0, cy0, cx0 + cam_size, cy0 + cam_size], radius=int(22 * scale), outline=(80, 42, 22), width=3, fill=(20, 22, 26))

    # Subtle MagSafe Magnetic Ring & Orientation Line
    m_r = int(48 * scale)
    draw.ellipse([cx - m_r, cy - m_r + int(20 * scale), cx + m_r, cy + m_r + int(20 * scale)], outline=(145, 82, 44), width=2)
    draw.line([cx, cy + int(72 * scale), cx, cy + int(96 * scale)], fill=(145, 82, 44), width=2)


# ==============================================================================
# IMAGE DISPATCHER (Strictly PNG)
# ==============================================================================

def generate_hardware_png(width, height, item_type, title, subtitle="", color_theme="titanium"):
    """
    Generate high-resolution, perfectly tailored PNG images for products, categories, or banners.
    Outputs strict PNG byte buffers.
    """
    # Palette definition for ambient studio canvas
    palettes = {
        "titanium": ((14, 18, 26), (6, 8, 12)),
        "ultramarine": ((12, 22, 42), (5, 9, 18)),
        "space_black": ((18, 18, 22), (6, 7, 9)),
        "silver": ((22, 24, 30), (8, 9, 13)),
        "purple": ((24, 14, 36), (8, 4, 14)),
        "emerald": ((10, 26, 20), (3, 12, 9)),
        "saddle": ((28, 16, 10), (10, 6, 4)),
    }
    top_c, bot_c = palettes.get(color_theme, palettes["titanium"])
    img = create_radial_gradient_canvas(width, height, top_c, bot_c)
    draw = ImageDraw.Draw(img)

    # Center drawing origin
    cx, cy = width // 2, height // 2

    # Draw specific hardware model
    if item_type == "phone_pro":
        draw_phone(draw, cx, cy - 25, scale=1.0, is_pro=True, color_theme="titanium")
    elif item_type == "phone_neo":
        draw_phone(draw, cx, cy - 25, scale=1.0, is_pro=False, color_theme="ultramarine")
    elif item_type == "laptop_pro":
        draw_laptop(draw, cx, cy - 20, scale=1.0, color_theme="space_black")
    elif item_type == "laptop_air":
        draw_laptop(draw, cx, cy - 20, scale=0.92, color_theme="space_black")
    elif item_type == "laptop_studio":
        draw_laptop(draw, cx, cy - 20, scale=0.96, color_theme="silver")
    elif item_type == "earbuds":
        draw_earbuds(draw, cx, cy - 25, scale=1.0)
    elif item_type == "headphones":
        draw_headphones(draw, cx, cy - 25, scale=1.0)
    elif item_type == "speaker":
        draw_speaker(draw, cx, cy - 25, scale=1.0)
    elif item_type == "wireless_charger":
        draw_wireless_charger(draw, cx, cy - 25, scale=1.0)
    elif item_type == "leather_case":
        draw_leather_case(draw, cx, cy - 25, scale=1.0)
    elif item_type == "cat_phones":
        draw_phone(draw, cx, cy - 25, scale=1.0, is_pro=True, color_theme="titanium")
    elif item_type == "cat_laptops":
        draw_laptop(draw, cx, cy - 20, scale=0.98, color_theme="space_black")
    elif item_type == "cat_audio":
        draw_headphones(draw, cx, cy - 25, scale=1.0)
    elif item_type == "cat_accessories":
        draw_wireless_charger(draw, cx, cy - 25, scale=1.0)
    elif item_type == "banner_laptop":
        # Wide Banner Layout (1600x900)
        draw_laptop(draw, int(width * 0.65), cy, scale=1.35, color_theme="space_black")
    elif item_type == "banner_phone":
        draw_phone(draw, int(width * 0.68), cy, scale=1.35, is_pro=True, color_theme="titanium")
    elif item_type == "banner_audio":
        draw_headphones(draw, int(width * 0.65), cy, scale=1.35)

    # Hardware Typographic Labels on Canvas Bottom
    if not item_type.startswith("banner_"):
        font_title = get_font(size=max(18, min(width // 24, 32)), bold=True)
        font_sub = get_font(size=max(12, min(width // 42, 16)), bold=False)

        # Title
        t_clean = title.strip()
        try:
            bbox_t = draw.textbbox((0, 0), t_clean, font=font_title)
            tw = bbox_t[2] - bbox_t[0]
        except Exception:
            tw = len(t_clean) * 12
        draw.text(((width - tw) // 2, height - (85 if height >= 600 else 55)), t_clean, fill=(255, 255, 255), font=font_title)

        # Subtitle
        s_clean = subtitle.strip() if subtitle else "VCART CERTIFIED ORIGINAL"
        try:
            bbox_s = draw.textbbox((0, 0), s_clean, font=font_sub)
            sw = bbox_s[2] - bbox_s[0]
        except Exception:
            sw = len(s_clean) * 8
        draw.text(((width - sw) // 2, height - (50 if height >= 600 else 32)), s_clean, fill=(148, 163, 184), font=font_sub)

        # Top-Left Logo Badge
        draw.rounded_rectangle([28, 28, 102, 56], radius=8, outline=(70, 80, 95), width=1, fill=(15, 18, 24))
        draw.text((42, 35), "VCART", fill=(56, 189, 248), font=get_font(size=12, bold=True))

    # Save Strictly as PNG
    buffer = io.BytesIO()
    img.save(buffer, format='PNG', optimize=True)
    slug = slugify(title)[:45]
    return ContentFile(buffer.getvalue(), name=f"{slug}.png")


# ==============================================================================
# MANAGEMENT COMMAND
# ==============================================================================

class Command(BaseCommand):
    help = "Seed database with Categories, Products, Banners, and Test User with clean, correct PNG placeholder images."

    def add_arguments(self, parser):
        parser.add_argument(
            '--refresh-images',
            action='store_true',
            help='Force regenerate all placeholder images even if already present.'
        )

    def handle(self, *args, **options):
        refresh_images = options.get('refresh_images', False)
        self.stdout.write(self.style.MIGRATE_HEADING("=== Starting Vcart Seed Data (Strict PNG Images) ==="))

        # ----------------------------------------------------------------------
        # 1. TEST USER
        # ----------------------------------------------------------------------
        self.stdout.write(self.style.HTTP_INFO("\n[1/4] Ensuring test user..."))
        test_user, user_created = User.objects.get_or_create(username=TEST_USER_USERNAME)
        test_user.email = TEST_USER_EMAIL
        test_user.first_name = TEST_USER_FIRST_NAME
        test_user.last_name = TEST_USER_LAST_NAME
        test_user.is_active = True
        test_user.set_password(TEST_USER_PASSWORD)
        test_user.save()

        action = "Created" if user_created else "Updated"
        self.stdout.write(
            self.style.SUCCESS(
                f"  -> {action} test user:\n"
                f"     Username: {TEST_USER_USERNAME}\n"
                f"     Password: {TEST_USER_PASSWORD}\n"
                f"     Email:    {TEST_USER_EMAIL}"
            )
        )

        # ----------------------------------------------------------------------
        # 2. CATEGORIES (4 categories with correct PNGs)
        # ----------------------------------------------------------------------
        self.stdout.write(self.style.HTTP_INFO("\n[2/4] Seeding 4 categories..."))
        categories_data = [
            {
                "name": "Phones",
                "slug": "phones",
                "description": "Flagship smartphones engineered for next-generation speed, pro optics, and all-day power.",
                "item_type": "cat_phones",
                "theme": "titanium",
            },
            {
                "name": "Laptops",
                "slug": "laptops",
                "description": "Pro workstations and ultra-light notebooks built for creators, coders, and power users.",
                "item_type": "cat_laptops",
                "theme": "space_black",
            },
            {
                "name": "Audio",
                "slug": "audio",
                "description": "High-fidelity acoustics, studio monitors, and active noise-canceling personal audio.",
                "item_type": "cat_audio",
                "theme": "silver",
            },
            {
                "name": "Accessories",
                "slug": "accessories",
                "description": "Precision magnetic chargers, protective cases, and premium everyday essentials.",
                "item_type": "cat_accessories",
                "theme": "titanium",
            },
        ]

        categories_map = {}
        for cat_info in categories_data:
            cat_defaults = {
                "name": cat_info["name"],
                "description": cat_info["description"],
                "is_active": True,
            }
            category, cat_created = Category.objects.get_or_create(slug=cat_info["slug"], defaults=cat_defaults)
            if not cat_created:
                category.name = cat_info["name"]
                category.description = cat_info["description"]
                category.is_active = True

            # Generate strictly PNG category showcase
            if refresh_images or not category.image or not category.image.name.endswith('.png'):
                png_file = generate_hardware_png(
                    width=800,
                    height=800,
                    item_type=cat_info["item_type"],
                    title=cat_info["name"],
                    subtitle="COLLECTION SHOWCASE",
                    color_theme=cat_info["theme"],
                )
                category.image.save(f"cat_{cat_info['slug']}.png", png_file, save=False)

            category.save()
            categories_map[cat_info["slug"]] = category
            act = "Created" if cat_created else "Updated"
            self.stdout.write(f"  -> {act} Category: {category.name}")

        # ----------------------------------------------------------------------
        # 3. PRODUCTS (10 products with individually tailored PNG illustrations)
        # ----------------------------------------------------------------------
        self.stdout.write(self.style.HTTP_INFO("\n[3/4] Seeding 10 original products with tailored PNGs..."))
        products_data = [
            # Phones
            {
                "name": "V-Phone 16 Pro",
                "slug": "v-phone-16-pro",
                "category": categories_map["phones"],
                "price": Decimal("134900.00"),
                "is_featured": True,
                "is_active": True,
                "key_specs": "Titanium chassis, A18 Pro chip, 48MP Fusion camera, 120Hz ProMotion",
                "description": (
                    "Engineered from aerospace-grade titanium with the industry-leading A18 Pro processor.\n\n"
                    "Features a revolutionary 48MP triple-lens optical camera system, customizable Action Button, "
                    "and next-generation battery optimization delivering all-day pro endurance."
                ),
                "item_type": "phone_pro",
                "theme": "titanium",
            },
            {
                "name": "V-Phone 16 Neo",
                "slug": "v-phone-16-neo",
                "category": categories_map["phones"],
                "price": Decimal("79900.00"),
                "is_featured": False,
                "is_active": True,
                "key_specs": "Aerospace aluminum, A18 Bionic, Action Button, 26-hr battery",
                "description": (
                    "Remarkably vibrant OLED Super Retina display with intelligent camera control, "
                    "color-infused back glass, and seamless USB-C fast charging.\n\n"
                    "Packed with cutting-edge performance in a light, ergonomic profile."
                ),
                "item_type": "phone_neo",
                "theme": "ultramarine",
            },

            # Laptops
            {
                "name": "AeroBook Pro 16",
                "slug": "aerobook-pro-16",
                "category": categories_map["laptops"],
                "price": Decimal("199900.00"),
                "is_featured": True,
                "is_active": True,
                "key_specs": "M3 Max processor, 36GB Unified Memory, Liquid Retina XDR, 22-hr battery",
                "description": (
                    "The most capable workstation laptop ever constructed. Built for intensive software compilation, "
                    "8K ProRes video rendering, and extreme creative multitasking.\n\n"
                    "Features the breathtaking Liquid Retina XDR display with 1600 nits peak brightness and studio-grade mics."
                ),
                "item_type": "laptop_pro",
                "theme": "space_black",
            },
            {
                "name": "AeroBook Air 14",
                "slug": "aerobook-air-14",
                "category": categories_map["laptops"],
                "price": Decimal("114900.00"),
                "is_featured": True,
                "is_active": True,
                "key_specs": "M3 chip, Fanless silent architecture, 1.24kg ultra-light, 18-hr battery",
                "description": (
                    "Impossibly thin, whisper quiet, and blazing fast. The AeroBook Air 14 delivers phenomenal all-day "
                    "efficiency in a stunning unibody aluminum design.\n\n"
                    "Perfect for students, traveling professionals, and everyday productivity."
                ),
                "item_type": "laptop_air",
                "theme": "space_black",
            },
            {
                "name": "AeroBook Studio 15",
                "slug": "aerobook-studio-15",
                "category": categories_map["laptops"],
                "price": Decimal("149900.00"),
                "is_featured": False,
                "is_active": True,
                "key_specs": "M3 Pro chip, 18GB Unified Memory, Spatial Audio, 1080p FaceTime HD",
                "description": (
                    "A balanced powerhouse designed for digital designers and audio engineers who demand sustained throughput.\n\n"
                    "Featuring high-bandwidth memory, MagSafe charging, three Thunderbolt 4 ports, and an SDXC card slot."
                ),
                "item_type": "laptop_studio",
                "theme": "silver",
            },

            # Audio
            {
                "name": "Pulse Buds Studio",
                "slug": "pulse-buds-studio",
                "category": categories_map["audio"],
                "price": Decimal("24900.00"),
                "is_featured": True,
                "is_active": True,
                "key_specs": "Active Noise Cancellation 2.0, Personalized Spatial Audio, MagSafe Case",
                "description": (
                    "Industry-leading acoustic architecture with pro-level Active Noise Cancellation and adaptive transparency.\n\n"
                    "Experience personalized spatial audio with dynamic head tracking that places sound all around you in three dimensions."
                ),
                "item_type": "earbuds",
                "theme": "silver",
            },
            {
                "name": "Pulse SoundMax Pro",
                "slug": "pulse-soundmax-pro",
                "category": categories_map["audio"],
                "price": Decimal("54900.00"),
                "is_featured": True,
                "is_active": True,
                "key_specs": "Custom 40mm dynamic drivers, Memory foam ear cushions, 30-hr playtime",
                "description": (
                    "Over-ear luxury headphones engineered with lossless studio clarity, stainless steel headband arms, and "
                    "tactile digital crown volume control.\n\n"
                    "Delivers an uncompromising acoustic experience from deep, resonant bass to crystalline highs."
                ),
                "item_type": "headphones",
                "theme": "silver",
            },
            {
                "name": "Pulse Mini Speaker",
                "slug": "pulse-mini-speaker",
                "category": categories_map["audio"],
                "price": Decimal("9900.00"),
                "is_featured": False,
                "is_active": True,
                "key_specs": "360-degree acoustic waveguide, Siri integration, IP67 waterproof",
                "description": (
                    "Compact wireless speaker delivering unexpectedly rich 360-degree room-filling sound, seamless stereo pairing, "
                    "and rugged water resistance for home or outdoor listening."
                ),
                "item_type": "speaker",
                "theme": "titanium",
            },

            # Accessories
            {
                "name": "MagDock Duo Wireless",
                "slug": "magdock-duo-wireless",
                "category": categories_map["accessories"],
                "price": Decimal("12900.00"),
                "is_featured": False,
                "is_active": True,
                "key_specs": "15W fast wireless charging, Foldable travel hinge, Aluminum finish",
                "description": (
                    "Simultaneously fast-charges your phone and smartwatch with precision magnetic alignment and rapid thermal management.\n\n"
                    "Folds compactly for convenient travel and desktop organization."
                ),
                "item_type": "wireless_charger",
                "theme": "titanium",
            },
            {
                "name": "V-Shield Leather Case",
                "slug": "v-shield-leather-case",
                "category": categories_map["accessories"],
                "price": Decimal("4900.00"),
                "is_featured": False,
                "is_active": True,
                "key_specs": "Supple European leather, Built-in magnets, Anodized aluminum buttons",
                "description": (
                    "Specially tanned and finished European leather that develops a natural patina over time.\n\n"
                    "Features precision machined aluminum buttons and integrated magnets aligned perfectly with MagDock chargers."
                ),
                "item_type": "leather_case",
                "theme": "saddle",
            },
        ]

        for p_info in products_data:
            p_defaults = {
                "name": p_info["name"],
                "category": p_info["category"],
                "price": p_info["price"],
                "is_featured": p_info["is_featured"],
                "is_active": p_info["is_active"],
                "key_specs": p_info["key_specs"],
                "description": p_info["description"],
            }
            product, prod_created = Product.objects.get_or_create(slug=p_info["slug"], defaults=p_defaults)
            if not prod_created:
                for k, v in p_defaults.items():
                    setattr(product, k, v)

            # Generate strictly PNG image
            if refresh_images or not product.image or not product.image.name.endswith('.png'):
                png_file = generate_hardware_png(
                    width=800,
                    height=800,
                    item_type=p_info["item_type"],
                    title=p_info["name"],
                    subtitle=p_info["key_specs"][:40],
                    color_theme=p_info["theme"],
                )
                product.image.save(f"prod_{p_info['slug']}.png", png_file, save=False)

            product.save()
            act = "Created" if prod_created else "Updated"
            featured_tag = "[FEATURED]" if product.is_featured else "          "
            self.stdout.write(f"  -> {act} {featured_tag} Product: {product.name} (Rs. {product.price})")

        # ----------------------------------------------------------------------
        # 4. BANNERS (3 Banners with high-res panoramic PNGs)
        # ----------------------------------------------------------------------
        self.stdout.write(self.style.HTTP_INFO("\n[4/4] Seeding 3 promotional banners with high-res PNGs..."))
        banners_data = [
            {
                "title": "AeroBook Pro 16. Pure Genius.",
                "subtitle": "Powered by M3 Max silicon with extreme dynamic range Liquid Retina XDR display and 22-hour battery life.",
                "button_text": "Order Now",
                "button_link": "/product/aerobook-pro-16/",
                "order": 1,
                "item_type": "banner_laptop",
                "theme": "space_black",
            },
            {
                "title": "V-Phone 16 Pro. Titanium.",
                "subtitle": "Forged in aerospace titanium with revolutionary A18 Pro silicon and pro optical camera controls.",
                "button_text": "Discover",
                "button_link": "/product/v-phone-16-pro/",
                "order": 2,
                "item_type": "banner_phone",
                "theme": "titanium",
            },
            {
                "title": "Pulse SoundMax Pro. Studio Fidelity.",
                "subtitle": "Custom 40mm dynamic drivers and lossless spatial audio with dynamic head tracking.",
                "button_text": "Experience",
                "button_link": "/product/pulse-soundmax-pro/",
                "order": 3,
                "item_type": "banner_audio",
                "theme": "silver",
            },
        ]

        # Deactivate any legacy/empty banners so only the 3 correct banners are active
        seed_titles = [b["title"] for b in banners_data]
        Banner.objects.exclude(title__in=seed_titles).update(is_active=False)

        for b_info in banners_data:
            b_defaults = {
                "subtitle": b_info["subtitle"],
                "button_text": b_info["button_text"],
                "button_link": b_info["button_link"],
                "order": b_info["order"],
                "is_active": True,
            }
            banner, b_created = Banner.objects.get_or_create(title=b_info["title"], defaults=b_defaults)
            if not b_created:
                for k, v in b_defaults.items():
                    setattr(banner, k, v)

            # Generate strictly PNG banner
            if refresh_images or not banner.image or not banner.image.name.endswith('.png'):
                png_file = generate_hardware_png(
                    width=1400,
                    height=800,
                    item_type=b_info["item_type"],
                    title=b_info["title"],
                    subtitle=b_info["subtitle"][:65],
                    color_theme=b_info["theme"],
                )
                banner.image.save(f"banner_{b_info['order']}.png", png_file, save=False)

            banner.save()
            act = "Created" if b_created else "Updated"
            self.stdout.write(f"  -> {act} Banner #{banner.order}: {banner.title}")

        self.stdout.write(self.style.SUCCESS("\n[SUCCESS] Seed data completed safely with 100% correct PNG images!"))
