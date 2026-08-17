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
        return response.json()["choices"][0]["message"]["content"]

    @staticmethod
    def generate_caption(topic):
        prompt = f"""
        Buat konten Instagram viral untuk topik: {topic}

        Output dalam format JSON dengan field:
        {{
            "title": "...",
            "caption": "...",
            "hashtags": "...",
            "cta": "...",
            "image_prompt": "..."
        }}

        Hashtag harus 15 hashtag yang relevan dan populer.
        Image prompt harus deskripsi visual untuk AI image generator.
        """
        content = AIService._call_ai([{"role": "user", "content": prompt}])
        return AIService._parse_json(content)

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
        image_response = requests.get(image_url, timeout=60)
        image_response.raise_for_status()
        return image_response.content, image_url


class InstagramAutomationService:
    @staticmethod
    def _get_browser_context():
        storage_path = str(settings.INSTAGRAM_SESSION_PATH)
        storage_dir = os.path.dirname(storage_path)
        os.makedirs(storage_dir, exist_ok=True)

        p = sync_playwright().start()
        browser = p.chromium.launch(headless=False)
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
            return False
        finally:
            context.close()
            browser.close()
            p.stop()
