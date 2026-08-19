import json
import os
import time
from pathlib import Path
from django.conf import settings
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import requests


class AIService:
    @staticmethod
    def _call_ai(messages, model=None):
        model = model or settings.AI_MODEL
        try:
            response = requests.post(
                f"{settings.AI_API_BASE}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.AI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": messages,
                },
                timeout=120,
            )
            response.raise_for_status()
            data = AIService._parse_response_json(response)
            if "choices" not in data or not data["choices"]:
                raise ValueError("AI response missing 'choices'")
            choice = data["choices"][0]
            if "message" not in choice or "content" not in choice["message"]:
                raise ValueError("AI response missing 'message.content'")
            return choice["message"]["content"]
        except Exception as e:
            print(f"AI Router fallback: {e}")
            topic = messages[-1]["content"] if messages else "general"
            if "hidup" in topic.lower() or "motivasi" in topic.lower() or "kehidupan" in topic.lower():
                category = "hidup"
            elif "ai" in topic.lower() or "teknologi" in topic.lower():
                category = "ai"
            elif "zodiak" in topic.lower() or "astrologi" in topic.lower() or "aquarius" in topic.lower():
                category = "astrology"
            else:
                category = "hidup"
            import json
            return json.dumps({
                "title": topic[:30],
                "caption": f"Quote inspirasi tentang {topic}. Setiap hari adalah kesempatan baru untuk berkembang.",
                "hashtags": f"#{topic.replace(' ', '')} #motivasi #inspirasi #hidup #quotes #viral #trending #instagram #positif #sukses",
                "cta": "Follow untuk lebih banyak inspirasi!",
                "image_prompt": f"Esthetic {category} quote image about {topic}, vibrant colors, modern design",
                "category": category
            })

    @staticmethod
    def _parse_response_json(response):
        import json
        import re
        text = response.text
        # Strip SSE framing: server appends "data: [DONE]" or sends "data: {...}" lines
        sse_lines = []
        for line in text.splitlines():
            line = line.strip()
            if line.startswith("data: ") and line != "data: [DONE]":
                sse_lines.append(line[6:])
        if sse_lines:
            text = "".join(sse_lines)
        # Some servers stream multiple chunks that form one JSON object
        text = text.replace("data: ", "")
        text = text.replace("[DONE]", "")
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
        return json.loads(text)

    TOPIC_CATEGORY = {
    "hidup": "hidup",
    "life": "hidup",
    "motivasi": "hidup",
    "inspirasi": "hidup",
    "kesedihan": "hidup",
    "kebahagiaan": "hidup",
    "cinta": "hidup",
    "persahabatan": "hidup",
    "ai": "ai",
    "teknologi": "ai",
    "robot": "ai",
    "machine learning": "ai",
    "deep learning": "ai",
    "astrology": "astrology",
    "zodiak": "astrology",
    "horoscope": "astrology",
    "bintang": "astrology",
    "ramalan": "astrology",
    "pisces": "astrology",
    "aries": "astrology",
    "taurus": "astrology",
    "gemini": "astrology",
    "cancer": "astrology",
    "leo": "astrology",
    "virgo": "astrology",
    "libra": "astrology",
    "scorpio": "astrology",
    "sagittarius": "astrology",
    "capricorn": "astrology",
    "aquarius": "astrology",
}

    @staticmethod
    def classify_topic(topic):
        """Detect category: hidup, ai, or astrology."""
        t = topic.lower().strip()
        for key, cat in AIService.TOPIC_CATEGORY.items():
            if key in t:
                return cat
        return "hidup"  # default

    @staticmethod
    def generate_caption(topic):
        category = AIService.classify_topic(topic)
        prompts = {
            "hidup": f"""
Buat 1 quote/motto tentang hidup dengan topik: {topic}.
Quote harus pendek (maks 2 kalimat), dalam Bahasa Indonesia, memotivasi.

Output JSON:
{{
    "title": "Judul singkat (maks 6 kata)",
    "caption": "Quote/motto lengkap. Bersih, pendek, powerful.",
    "hashtags": "15 hashtag relevan tentang motivasi/kehidupan",
    "cta": "CTA untuk comment/share",
    "image_prompt": "Deskripsi gambar estetik untuk quote ini, dalam bahasa Inggris",
    "category": "hidup"
}}""",
            "ai": f"""
Buat 1 quote tentang AI/teknologi dengan topik: {topic}.
Quote harus pendek (maks 2 kalimat), dalam Bahasa Indonesia, visioner.

Output JSON:
{{
    "title": "Judul singkat (maks 6 kata)",
    "caption": "Quote tentang AI/teknologi. Futuristik, menyentuh, relatable.",
    "hashtags": "15 hashtag relevan tentang AI/teknologi",
    "cta": "CTA untuk follow/comment",
    "image_prompt": "Deskripsi gambar futuristik untuk quote ini, dalam bahasa Inggris",
    "category": "ai"
}}""",
            "astrology": f"""
Buat 1 quote/motto tentang astrologi dengan topik: {topic}.
Quote harus pendek (maks 2 kalimat), dalam Bahasa Indonesia, misterius & aesthetic.

Output JSON:
{{
    "title": "Judul singkat (maks 6 kata)",
    "caption": "Quote astrologi. Mystical, aesthetic, menyentuh hati.",
    "hashtags": "15 hashtag relevan tentang astrologi/zodiak",
    "cta": "CTA untuk tag teman zodiak",
    "image_prompt": "Deskripsi gambar kosmik/misterius untuk quote ini, dalam bahasa Inggris",
    "category": "astrology"
}}""",
        }
        prompt = prompts.get(category, prompts["hidup"])
        content = AIService._call_ai([{"role": "user", "content": prompt}])
        result = AIService._parse_json(content)
        result["category"] = category
        result["topic"] = topic
        return result

    @staticmethod
    def _parse_json(content):
        import json
        import re
        try:
            match = re.search(r"\{.*\}", content, re.DOTALL)
            if match:
                return json.loads(match.group())
            return json.loads(content)
        except Exception:
            return {
                "title": content[:100],
                "caption": content,
                "hashtags": "#viral #trending #instagram",
                "cta": "Follow for more!",
                "image_prompt": "Modern social media design, vibrant colors",
            }

    @staticmethod
    def generate_image(prompt):
        try:
            response = requests.post(
                f"{settings.AI_API_BASE}/images/generations",
                headers={
                    "Authorization": f"Bearer {settings.AI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.AI_IMAGE_MODEL,
                    "prompt": prompt,
                    "n": 1,
                    "size": "1024x1024",
                },
                timeout=120,
            )
            response.raise_for_status()
            data = response.json()
            image_url = data["data"][0]["url"]
            img_response = requests.get(image_url, timeout=60)
            img_response.raise_for_status()
            return img_response.content, image_url
        except Exception as e:
            print(f"Image generation fallback: {e}")
            return AIService._generate_placeholder_image(prompt)

    @staticmethod
    def _generate_placeholder_image(text, category="hidup"):
        """1024x1024 themed quote image — gradient per category + wrapped text."""
        from PIL import Image as PILImage, ImageDraw, ImageFont
        import io, math, random

        palettes = {
            "hidup": [
                ((255, 111, 97), (255, 154, 158)),
                ((255, 94, 98), (255, 140, 105)),
                ((255, 99, 132), (255, 159, 243)),
                ((254, 202, 202), (255, 159, 243)),
                ((255, 154, 158), (255, 182, 193)),
                ((255, 99, 72), (255, 127, 80)),
            ],
            "ai": [
                ((76, 0, 255), (0, 229, 255)),
                ((0, 0, 255), (0, 255, 255)),
                ((72, 0, 255), (0, 255, 200)),
                ((30, 0, 255), (180, 0, 255)),
                ((0, 255, 255), (0, 100, 255)),
                ((120, 0, 255), (0, 200, 255)),
            ],
            "astrology": [
                ((45, 27, 96), (119, 47, 157)),
                ((72, 0, 255), (180, 0, 255)),
                ((20, 0, 80), (120, 0, 150)),
                ((40, 0, 100), (100, 0, 180)),
                ((25, 25, 112), (138, 43, 226)),
                ((48, 25, 100), (160, 60, 200)),
            ],
        }
        palette = palettes.get(category, palettes["hidup"])
        start, end = random.choice(palette)

        def jitter(color, amount=20):
            return tuple(max(0, min(255, c + random.randint(-amount, amount))) for c in color)

        start = jitter(start, 25)
        end = jitter(end, 25)

        labels = {
            "hidup": "LIFE QUOTES",
            "ai": "AI INSIGHT",
            "astrology": "COSMIC WISDOM",
        }
        label = labels.get(category, "QUOTE")
        accent = (255, 255, 255)

        img = PILImage.new("RGB", (1024, 1024))
        draw_bg = ImageDraw.Draw(img)
        for y in range(1024):
            t = y / 1024
            r = int(start[0] + (end[0] - start[0]) * t)
            g = int(start[1] + (end[1] - start[1]) * t)
            b = int(start[2] + (end[2] - start[2]) * t)
            draw_bg.line([(0, y), (1024, y)], fill=(r, g, b))

        overlay = PILImage.new("RGBA", (1024, 1024), (0, 0, 0, 0))
        draw_ov = ImageDraw.Draw(overlay)
        seed = hash(text) % 10000
        random.seed(seed)
        for _ in range(6):
            cx = random.randint(0, 1024)
            cy = random.randint(0, 1024)
            radius = random.randint(40, 180)
            alpha = random.randint(15, 40)
            draw_ov.ellipse(
                [cx - radius, cy - radius, cx + radius, cy + radius],
                fill=(255, 255, 255, alpha),
            )
        if category == "astrology":
            for _ in range(80):
                sx, sy = random.randint(0, 1024), random.randint(0, 1024)
                sr = random.randint(1, 3)
                draw_ov.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 255, 200, 200))
        elif category == "ai":
            for _ in range(30):
                sx, sy = random.randint(0, 1024), random.randint(0, 1024)
                draw_ov.ellipse([sx - 5, sy - 5, sx + 5, sy + 5], fill=(0, 255, 255, 100))
        img = PILImage.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

        draw = ImageDraw.Draw(img)
        font = None
        font_small = None
        for fname in ("arial.ttf", "segoeui.ttf", "trebuc.ttf"):
            try:
                font = ImageFont.truetype(fname, 40)
                font_small = ImageFont.truetype(fname, 22)
                break
            except Exception:
                continue
        if font is None:
            font = ImageFont.load_default()
            font_small = font

        draw.rectangle([112, 880, 912, 884], fill=accent + (255,) if len(accent) == 3 else accent)

        words = text.split()
        lines = []
        current_line = []
        for word in words:
            test_line = " ".join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] <= 850:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
        if current_line:
            lines.append(" ".join(current_line))
        lines = lines[:6]
        display_text = "\n".join(lines) if lines else text

        bbox = draw.textbbox((0, 0), display_text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        x = (1024 - text_w) / 2
        y = 320 + (360 - text_h) / 2

        draw.text((x + 2, y + 2), display_text, font=font, fill=(0, 0, 0, 120))
        draw.text((x, y), display_text, font=font, fill=(255, 255, 255, 255))

        draw.text((512, 900), label, font=font_small, fill=(255, 255, 255, 220), anchor="mm")

        buf = io.BytesIO()
        img.save(buf, format="PNG", optimize=True)
        return buf.getvalue(), "placeholder"


class InstagramAutomationService:
    @staticmethod
    def _get_browser_context():
        storage_path = str(settings.INSTAGRAM_SESSION_PATH)
        storage_dir = os.path.dirname(storage_path)
        os.makedirs(storage_dir, exist_ok=True)

        p = sync_playwright().start()
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )
        if os.path.exists(storage_path):
            try:
                with open(storage_path, "r") as f:
                    storage_state = json.load(f)
                context.add_cookies(storage_state)
            except Exception:
                pass
        return p, browser, context

    @staticmethod
    def _save_session(context):
        storage_path = str(settings.INSTAGRAM_SESSION_PATH)
        try:
            state = context.storage_state()
            with open(storage_path, "w") as f:
                json.dump(state, f)
        except Exception as e:
            print(f"Failed to save session: {e}")

    @staticmethod
    def login(page):
        page.goto("https://www.instagram.com/accounts/login/", wait_until="domcontentloaded")
        page.wait_for_timeout(3000)
        if "login" not in page.url:
            return True

        username_input = page.locator('input[name="username"]')
        password_input = page.locator('input[name="password"]')
        username_input.fill(settings.INSTAGRAM_USERNAME)
        password_input.fill(settings.INSTAGRAM_PASSWORD)

        page.click('button[type="submit"]')
        page.wait_for_timeout(5000)

        try:
            page.wait_for_selector('input[name="username"]', timeout=3000)
            page.locator('input[name="username"]').fill(settings.INSTAGRAM_USERNAME)
            verification_code = input("Enter Instagram verification code: ")
            page.locator('input[name="verificationCode"]').fill(verification_code)
            page.click('button[type="submit"]')
            page.wait_for_timeout(5000)
        except PlaywrightTimeout:
            pass

        return "challenge" not in page.url and "login" not in page.url

    @staticmethod
    def publish_post(post):
        p, browser, context = InstagramAutomationService._get_browser_context()
        page = context.new_page()
        try:
            InstagramAutomationService.login(page)
            page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
            page.wait_for_timeout(3000)

            if post.image:
                image_path = os.path.join(settings.MEDIA_ROOT, post.image.name)
                if not os.path.exists(image_path):
                    image_path = str(post.image.path)

                file_input = page.locator('input[type="file"]').first
                file_input.set_input_files(image_path)
                page.wait_for_timeout(5000)

                caption = f"{post.title}\n\n{post.caption}\n\n{post.hashtags}\n\n{post.caption.split(chr(10))[-1] if chr(10) in post.caption else ''}"

                try:
                    text_area = page.locator('div[contenteditable="true"]').first
                    text_area.fill(caption)
                except Exception:
                    try:
                        text_area = page.locator('textarea').first
                        text_area.fill(caption)
                    except Exception:
                        pass

                page.wait_for_timeout(2000)
                share_btn = page.locator('text=Share')
                if share_btn.count() > 0:
                    share_btn.first.click()
                else:
                    page.keyboard.press("Enter")
                page.wait_for_timeout(8000)
            else:
                page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
                page.wait_for_timeout(3000)
                create_btn = page.locator('text=Create')
                if create_btn.count() > 0:
                    create_btn.first.click()
                    page.wait_for_timeout(2000)
                    caption = f"{post.title}\n\n{post.caption}\n\n{post.hashtags}"
                    try:
                        text_area = page.locator('div[contenteditable="true"]').first
                        text_area.fill(caption)
                    except Exception:
                        text_area = page.locator('textarea').first
                        text_area.fill(caption)
                    page.wait_for_timeout(2000)
                    share_btn = page.locator('text=Share')
                    if share_btn.count() > 0:
                        share_btn.first.click()
                    else:
                        page.keyboard.press("Enter")
                    page.wait_for_timeout(8000)
                else:
                    raise Exception("Could not find Create button")

            InstagramAutomationService._save_session(context)
            return True
        except Exception as e:
            print(f"Instagram publish error: {e}")
            post.error_message = str(e)
            post.save()
            return False
        finally:
            context.close()
            browser.close()
            p.stop()
