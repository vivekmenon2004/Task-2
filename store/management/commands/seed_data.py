import io
import os
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
# PIL Image Generator Utilities (Clean, non-copyrighted placeholders)
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


def create_gradient_canvas(width, height, color_top, color_bottom):
    """Generate a vertical 2-stop color gradient."""
    base = Image.new('RGB', (width, height), color_top)
    top_r, top_g, top_b = color_top
    bot_r, bot_g, bot_b = color_bottom
    draw = ImageDraw.Draw(base)
    for y in range(height):
        ratio = y / max(1, height - 1)
        r = int(top_r + (bot_r - top_r) * ratio)
        g = int(top_g + (bot_g - top_g) * ratio)
        b = int(top_b + (bot_b - top_b) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    return base


def draw_device_illustration(draw, icon_type, center_x, center_y, accent_rgb=(0, 113, 227)):
    """Draw a minimalist vector-style hardware illustration."""
    if icon_type == 'phone':
        # Smartphone silhouette
        w, h = 130, 240
        x0, y0 = center_x - w // 2, center_y - h // 2
        x1, y1 = center_x + w // 2, center_y + h // 2
        # Outer body
        draw.rounded_rectangle([x0, y0, x1, y1], radius=28, outline=accent_rgb, width=4, fill=(15, 23, 42))
        # Inner screen
        draw.rounded_rectangle([x0 + 8, y0 + 10, x1 - 8, y1 - 10], radius=20, outline=(51, 65, 85), width=2, fill=(2, 6, 23))
        # Dynamic Island pill
        draw.rounded_rectangle([center_x - 22, y0 + 16, center_x + 22, y0 + 26], radius=5, fill=(15, 23, 42))
        # Home bar
        draw.rounded_rectangle([center_x - 30, y1 - 20, center_x + 30, y1 - 17], radius=2, fill=(100, 116, 139))

    elif icon_type == 'laptop':
        # Laptop silhouette
        screen_w, screen_h = 240, 150
        sx0, sy0 = center_x - screen_w // 2, center_y - 30 - screen_h // 2
        sx1, sy1 = center_x + screen_w // 2, center_y - 30 + screen_h // 2
        # Lid / Screen
        draw.rounded_rectangle([sx0, sy0, sx1, sy1], radius=14, outline=accent_rgb, width=4, fill=(15, 23, 42))
        draw.rounded_rectangle([sx0 + 8, sy0 + 8, sx1 - 8, sy1 - 8], radius=8, outline=(51, 65, 85), width=2, fill=(2, 6, 23))
        # Camera notch
        draw.ellipse([center_x - 3, sy0 + 3, center_x + 3, sy0 + 9], fill=accent_rgb)
        # Base keyboard chassis
        base_w, base_h = 280, 18
        bx0, by0 = center_x - base_w // 2, sy1
        bx1, by1 = center_x + base_w // 2, sy1 + base_h
        draw.rounded_rectangle([bx0, by0, bx1, by1], radius=6, outline=accent_rgb, width=3, fill=(30, 41, 59))
        # Trackpad notch
        draw.rounded_rectangle([center_x - 35, by0, center_x + 35, by0 + 4], radius=2, fill=(148, 163, 184))

    elif icon_type == 'audio':
        # Studio headphones silhouette
        r = 75
        # Headband arc
        draw.arc([center_x - r, center_y - r - 20, center_x + r, center_y + r - 20], start=180, end=0, fill=accent_rgb, width=8)
        # Headband cushion
        draw.arc([center_x - r + 8, center_y - r - 12, center_x + r - 8, center_y + r - 28], start=190, end=350, fill=(148, 163, 184), width=4)
        # Left ear cup
        draw.rounded_rectangle([center_x - r - 18, center_y - 25, center_x - r + 18, center_y + 45], radius=18, outline=accent_rgb, width=4, fill=(15, 23, 42))
        # Right ear cup
        draw.rounded_rectangle([center_x + r - 18, center_y - 25, center_x + r + 18, center_y + 45], radius=18, outline=accent_rgb, width=4, fill=(15, 23, 42))
        # Soundwave accent lines
        draw.line([center_x - 20, center_y + 10, center_x - 20, center_y + 25], fill=(56, 189, 248), width=3)
        draw.line([center_x, center_y + 2, center_x, center_y + 33], fill=accent_rgb, width=3)
        draw.line([center_x + 20, center_y + 10, center_x + 20, center_y + 25], fill=(56, 189, 248), width=3)

    else:
        # Accessory: MagSafe Magnetic Pad & Ring
        r = 70
        draw.ellipse([center_x - r, center_y - r, center_x + r, center_y + r], outline=accent_rgb, width=6, fill=(15, 23, 42))
        draw.ellipse([center_x - 36, center_y - 36, center_x + 36, center_y + 36], outline=(56, 189, 248), width=3, fill=(2, 6, 23))
        # Lightning / Charging Bolt
        bolt_points = [
            (center_x + 4, center_y - 22),
            (center_x - 12, center_y + 2),
            (center_x - 1, center_y + 2),
            (center_x - 4, center_y + 22),
            (center_x + 12, center_y - 2),
            (center_x + 1, center_y - 2),
        ]
        draw.polygon(bolt_points, fill=(250, 204, 21))


def generate_placeholder_image(width, height, title, subtitle="", icon_type="phone", color_theme="blue"):
    """
    Generate a sleek, modern placeholder image using Pillow.
    Returns a ContentFile ready to assign to Django ImageField.
    """
    theme_palettes = {
        "blue": {
            "top": (10, 15, 30),
            "bottom": (2, 6, 18),
            "accent": (0, 113, 227),
            "accent_light": (56, 189, 248),
        },
        "purple": {
            "top": (22, 12, 38),
            "bottom": (8, 4, 18),
            "accent": (147, 51, 234),
            "accent_light": (192, 132, 252),
        },
        "slate": {
            "top": (24, 28, 36),
            "bottom": (11, 13, 18),
            "accent": (99, 102, 241),
            "accent_light": (129, 140, 248),
        },
        "emerald": {
            "top": (10, 30, 24),
            "bottom": (3, 14, 11),
            "accent": (16, 185, 129),
            "accent_light": (52, 211, 153),
        },
    }

    palette = theme_palettes.get(color_theme, theme_palettes["blue"])
    img = create_gradient_canvas(width, height, palette["top"], palette["bottom"])
    draw = ImageDraw.Draw(img)

    # Ambient glow circle
    glow_radius = min(width, height) // 3
    glow_box = [
        width // 2 - glow_radius,
        height // 2 - 20 - glow_radius,
        width // 2 + glow_radius,
        height // 2 - 20 + glow_radius,
    ]
    draw.ellipse(glow_box, outline=palette["accent_light"], width=1)

    # Draw hardware illustration
    center_y = height // 2 - (35 if height >= 600 else 15)
    draw_device_illustration(draw, icon_type, width // 2, center_y, accent_rgb=palette["accent"])

    # Draw Title and Subtitle Text at the bottom
    font_title = get_font(size=max(18, min(width // 22, 34)), bold=True)
    font_sub = get_font(size=max(12, min(width // 40, 18)), bold=False)

    title_clean = title.strip()
    # Title
    try:
        bbox_t = draw.textbbox((0, 0), title_clean, font=font_title)
        t_w = bbox_t[2] - bbox_t[0]
    except Exception:
        t_w = len(title_clean) * 12
    draw.text(((width - t_w) // 2, height - (95 if height >= 600 else 60)), title_clean, fill=(255, 255, 255), font=font_title)

    # Subtitle or Brand mark
    sub_text = subtitle.strip() if subtitle else "VCART CERTIFIED PRODUCT"
    try:
        bbox_s = draw.textbbox((0, 0), sub_text, font=font_sub)
        s_w = bbox_s[2] - bbox_s[0]
    except Exception:
        s_w = len(sub_text) * 7
    draw.text(((width - s_w) // 2, height - (55 if height >= 600 else 35)), sub_text, fill=(148, 163, 184), font=font_sub)

    # Brand badge at top corner
    badge_font = get_font(size=12, bold=True)
    draw.rounded_rectangle([24, 24, 98, 52], radius=8, outline=palette["accent"], width=1, fill=(15, 23, 42))
    draw.text((38, 31), "VCART", fill=palette["accent_light"], font=badge_font)

    # Save to BytesIO
    buffer = io.BytesIO()
    img.save(buffer, format='PNG', optimize=True)
    slug = slugify(title)[:40]
    return ContentFile(buffer.getvalue(), name=f"{slug}.png")


# ==============================================================================
# Management Command
# ==============================================================================

class Command(BaseCommand):
    help = "Seed database with Categories, Products, Banners, and Test User with clean placeholder images."

    def add_arguments(self, parser):
        parser.add_argument(
            '--refresh-images',
            action='store_true',
            help='Force regenerate all placeholder images even if already present.'
        )

    def handle(self, *args, **options):
        refresh_images = options.get('refresh_images', False)
        self.stdout.write(self.style.MIGRATE_HEADING("=== Starting Vcart Seed Data ==="))

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
        # 2. CATEGORIES (4 categories)
        # ----------------------------------------------------------------------
        self.stdout.write(self.style.HTTP_INFO("\n[2/4] Seeding 4 categories..."))
        categories_data = [
            {
                "name": "Phones",
                "slug": "phones",
                "description": "Flagship smartphones engineered for next-generation speed, pro optics, and all-day power.",
                "icon": "phone",
                "theme": "blue",
            },
            {
                "name": "Laptops",
                "slug": "laptops",
                "description": "Pro workstations and ultra-light notebooks built for creators, coders, and power users.",
                "icon": "laptop",
                "theme": "slate",
            },
            {
                "name": "Audio",
                "slug": "audio",
                "description": "High-fidelity acoustics, studio monitors, and active noise-canceling personal audio.",
                "icon": "audio",
                "theme": "purple",
            },
            {
                "name": "Accessories",
                "slug": "accessories",
                "description": "Precision magnetic chargers, protective cases, and premium everyday essentials.",
                "icon": "accessory",
                "theme": "emerald",
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

            if refresh_images or not category.image:
                img_file = generate_placeholder_image(
                    width=600,
                    height=600,
                    title=cat_info["name"],
                    subtitle="CATEGORY SHOWCASE",
                    icon_type=cat_info["icon"],
                    color_theme=cat_info["theme"],
                )
                category.image.save(f"cat_{cat_info['slug']}.png", img_file, save=False)

            category.save()
            categories_map[cat_info["slug"]] = category
            act = "Created" if cat_created else "Updated"
            self.stdout.write(f"  -> {act} Category: {category.name}")

        # ----------------------------------------------------------------------
        # 3. PRODUCTS (10 products with original names & descriptions)
        # ----------------------------------------------------------------------
        self.stdout.write(self.style.HTTP_INFO("\n[3/4] Seeding 10 original products..."))
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
                "icon": "phone",
                "theme": "blue",
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
                "icon": "phone",
                "theme": "slate",
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
                "icon": "laptop",
                "theme": "blue",
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
                "icon": "laptop",
                "theme": "slate",
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
                "icon": "laptop",
                "theme": "purple",
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
                "icon": "audio",
                "theme": "purple",
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
                "icon": "audio",
                "theme": "blue",
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
                "icon": "audio",
                "theme": "slate",
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
                "icon": "accessory",
                "theme": "emerald",
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
                "icon": "accessory",
                "theme": "emerald",
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

            if refresh_images or not product.image:
                img_file = generate_placeholder_image(
                    width=800,
                    height=800,
                    title=p_info["name"],
                    subtitle=p_info["key_specs"][:40],
                    icon_type=p_info["icon"],
                    color_theme=p_info["theme"],
                )
                product.image.save(f"prod_{p_info['slug']}.png", img_file, save=False)

            product.save()
            act = "Created" if prod_created else "Updated"
            featured_tag = "[FEATURED]" if product.is_featured else "          "
            self.stdout.write(f"  -> {act} {featured_tag} Product: {product.name} (Rs. {product.price})")

        # ----------------------------------------------------------------------
        # 4. BANNERS (3 Banners)
        # ----------------------------------------------------------------------
        self.stdout.write(self.style.HTTP_INFO("\n[4/4] Seeding 3 promotional banners..."))
        banners_data = [
            {
                "title": "AeroBook Pro 16. Pure Genius.",
                "subtitle": "Powered by M3 Max silicon with extreme dynamic range Liquid Retina XDR display and 22-hour battery life.",
                "button_text": "Order Now",
                "button_link": "/product/aerobook-pro-16/",
                "order": 1,
                "icon": "laptop",
                "theme": "blue",
            },
            {
                "title": "V-Phone 16 Pro. Titanium.",
                "subtitle": "Forged in aerospace titanium with revolutionary A18 Pro silicon and pro optical camera controls.",
                "button_text": "Discover",
                "button_link": "/product/v-phone-16-pro/",
                "order": 2,
                "icon": "phone",
                "theme": "purple",
            },
            {
                "title": "Pulse SoundMax Pro. Studio Fidelity.",
                "subtitle": "Custom 40mm dynamic drivers and lossless spatial audio with dynamic head tracking.",
                "button_text": "Experience",
                "button_link": "/product/pulse-soundmax-pro/",
                "order": 3,
                "icon": "audio",
                "theme": "slate",
            },
        ]

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

            if refresh_images or not banner.image:
                img_file = generate_placeholder_image(
                    width=1200,
                    height=700,
                    title=b_info["title"],
                    subtitle=b_info["subtitle"][:65],
                    icon_type=b_info["icon"],
                    color_theme=b_info["theme"],
                )
                banner.image.save(f"banner_{b_info['order']}.png", img_file, save=False)

            banner.save()
            act = "Created" if b_created else "Updated"
            self.stdout.write(f"  -> {act} Banner #{banner.order}: {banner.title}")

        self.stdout.write(self.style.SUCCESS("\n[SUCCESS] Seed data completed safely!"))
