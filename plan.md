# Django Instagram AI Auto Content Generator

Sistem otomatis untuk membuat dan mempublikasikan konten Instagram menggunakan AI.

Fitur utama:

- Generate caption Instagram menggunakan AI
- Generate hashtag otomatis
- Generate prompt gambar otomatis
- Generate gambar menggunakan AI
- Menyimpan histori konten ke PostgreSQL
- Redis Cache
- Celery Scheduler
- Celery Beat
- Dashboard Django Admin
- Auto Publish Instagram menggunakan Playwright
- Approval Workflow
- Retry Failed Posting
- Multi Schedule Posting
- Logging & Monitoring

---

# Target Account

```text
Instagram Account
@jakarta24viral
```

---

# System Architecture

```text
Celery Beat
     │
     ▼
Generate Content Schedule
     │
     ▼
AI Router
(http://localhost:20128/v1)
     │
     ▼
Generate Title
     │
     ▼
Generate Caption
     │
     ▼
Generate Hashtags
     │
     ▼
Generate Image Prompt
     │
     ▼
Generate Image
     │
     ▼
Save PostgreSQL
     │
     ▼
Redis Cache
     │
     ▼
Content Queue
     │
     ▼
Playwright
     │
     ▼
Instagram Login
     │
     ▼
Auto Publish
     │
     ▼
Published
```

---

# Technology Stack

## Backend

- Django 5.x
- Django ORM
- PostgreSQL

## Queue

- Celery
- Celery Beat

## Cache

- Redis

## AI

- AI Router
- OpenAI Compatible API

## Automation

- Playwright

## Image

- Pillow

---

# Database Configuration

## PostgreSQL

```ini
HOST=localhost
PORT=5008
NAME=instagram_ai
USER=postgres
PASSWORD=YOUR_DATABASE_PASSWORD
```

Create Database

```sql
CREATE DATABASE instagram_ai;
```

---

# Redis Configuration

Install Redis

Ubuntu

```bash
sudo apt update
sudo apt install redis-server -y
```

Enable Service

```bash
sudo systemctl enable redis-server
```

Start Service

```bash
sudo systemctl start redis-server
```

Verify

```bash
redis-cli ping
```

Expected Output

```text
PONG
```

---

# Environment Variables

Create file:

```text
.env
```

```env
DEBUG=True

SECRET_KEY=replace_me

DB_NAME=instagram_ai
DB_USER=postgres
DB_PASSWORD=YOUR_DATABASE_PASSWORD
DB_HOST=localhost
DB_PORT=5008

REDIS_HOST=localhost
REDIS_PORT=6379

AI_API_BASE=http://localhost:20128/v1
AI_API_KEY=YOUR_API_KEY

INSTAGRAM_USERNAME=jakarta24viral
INSTAGRAM_PASSWORD=YOUR_INSTAGRAM_PASSWORD
```

---

# Install Dependencies

```bash
pip install django
pip install psycopg2-binary
pip install redis
pip install django-redis
pip install celery
pip install pillow
pip install python-dotenv
pip install openai
pip install playwright
pip install requests
```

Install Browser

```bash
playwright install chromium
```

---

# Django Settings

## PostgreSQL

```python
import os

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
    }
}
```

---

## Redis Cache

```python
CACHES = {
    "default": {
        "BACKEND":
            "django_redis.cache.RedisCache",

        "LOCATION":
            "redis://127.0.0.1:6379/1",

        "OPTIONS": {
            "CLIENT_CLASS":
            "django_redis.client.DefaultClient",
        }
    }
}
```

---

# Celery Configuration

## celery.py

```python
from celery import Celery

app = Celery("config")

app.conf.broker_url = \
    "redis://localhost:6379/0"

app.conf.result_backend = \
    "redis://localhost:6379/0"

app.autodiscover_tasks()
```

---

# Content Model

## posts/models.py

```python
from django.db import models


class Post(models.Model):

    STATUS_CHOICES = (

        ("draft", "Draft"),

        ("generated", "Generated"),

        ("scheduled", "Scheduled"),

        ("posting", "Posting"),

        ("published", "Published"),

        ("failed", "Failed"),
    )

    title = models.CharField(
        max_length=255
    )

    topic = models.TextField()

    caption = models.TextField()

    hashtags = models.TextField()

    image_prompt = models.TextField()

    image = models.ImageField(
        upload_to="posts/"
    )

    publish_at = models.DateTimeField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.title
```

---

# AI Router Configuration

Endpoint:

```text
http://localhost:20128/v1
```

Client

```python
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("AI_API_KEY"),
    base_url=os.getenv("AI_API_BASE"),
)
```

---

# AI Caption Generator

```python
def generate_caption(topic):

    response = client.chat.completions.create(
        model="gpt-4.1",

        messages=[
            {
                "role": "user",

                "content": f"""
                Buat konten Instagram viral.

                Topik:
                {topic}

                Output:

                1. Judul

                2. Caption

                3. 15 Hashtag

                4. CTA

                5. Prompt Gambar
                """
            }
        ]
    )

    return \
        response.choices[0].message.content
```

---

# Default Content Categories

```python
TOPICS = [

    "Berita Jakarta",

    "Wisata Jakarta",

    "Kuliner Jakarta",

    "Kata Kata Motivasi",

    "Fakta Unik Indonesia",

    "Tips Kehidupan",

    "Teknologi",

    "AI",

    "Digital Lifestyle",

    "Viral Indonesia",

]
```

---

# Example Image Prompt

```text
Jakarta skyline at sunset,
viral social media design,
modern typography area,
instagram square design,
news and trends layout,
professional lighting,
high quality,
social media engagement
```

---

# Auto Generate Task

```python
from celery import shared_task


@shared_task
def generate_content():

    topics = [

        "Jakarta Viral",

        "AI",

        "Teknologi",

        "Lifestyle",

        "Motivasi"
    ]

    for topic in topics:

        print(
            f"Generate {topic}"
        )
```

---

# Auto Publish Task

```python
from celery import shared_task


@shared_task
def auto_publish_post():

    print(
        "Posting to Instagram"
    )
```

---

# Celery Schedule

```python
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {

    "morning_post": {

        "task":
        "posts.tasks.auto_publish_post",

        "schedule":
        crontab(hour=8, minute=0)
    },

    "afternoon_post": {

        "task":
        "posts.tasks.auto_publish_post",

        "schedule":
        crontab(hour=13, minute=0)
    },

    "night_post": {

        "task":
        "posts.tasks.auto_publish_post",

        "schedule":
        crontab(hour=20, minute=0)
    }
}
```

---

# Instagram Automation

## Session Storage

```text
storage/
└── instagram_session.json
```

---

## Instagram Login

```python
from playwright.sync_api \
import sync_playwright


def login_instagram():

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False
        )

        context = browser.new_context()

        page = context.new_page()

        page.goto(
            "https://www.instagram.com/"
        )

        page.fill(
            'input[name="username"]',
            "jakarta24viral"
        )
```

---

# Folder Structure

```text
post-kata2-ig/

├── config/
│
├── posts/
│
├── scheduler/
│
├── ai/
│
├── storage/
│   └── instagram_session.json
│
├── templates/
│
├── static/
│
├── media/
│
├── logs/
│
├── manage.py
│
├── celery.py
│
├── requirements.txt
│
├── run.bat
│
├── push.bat
│
├── update.bat
│
├── .env
│
├── .gitignore
│
└── README.md
```

---

# run.bat

```bat
@echo off

echo ===================================
echo START DJANGO INSTAGRAM AI
echo ===================================

start cmd /k "redis-server"

timeout /t 3

start cmd /k "celery -A config worker -l info"

start cmd /k "celery -A config beat -l info"

start cmd /k "python manage.py runserver"

pause
```

---

# push.bat

```bat
@echo off

echo ===================================
echo PUSH TO GITHUB
echo ===================================

git init

git add .

git commit -m "Initial commit"

git remote remove origin 2>nul

git remote add origin https://github.com/harys-rifai/post-kata2-ig.git

git branch -M main

git push -u origin main

pause
```

---

# update.bat

```bat
@echo off

set /p msg=Commit Message:

git add .

git commit -m "%msg%"

git push origin main

pause
```

---

# Requirements

```txt
Django
psycopg2-binary
redis
django-redis
celery
python-dotenv
pillow
openai
playwright
requests
```

---

# .gitignore

```gitignore
.env

venv/
.venv/

__pycache__/
*.pyc

media/

logs*

.idea/

.vscode/

*.log
```

---*
#*First Run

Create Migration*
```bash
python manage.py makemigr*tions
```

```bash
python manage.p* migrate
```

Create Admin

```bas*
python manage.py createsuperuser
*``

Run Application*
```bash
run.bat
```

Or*
*``bash
python manage.py*runserver
```

---

# GitHub*Repository

```bash*git remote add origin https://github.com/harys-rifai/post-kata2-ig.git

git branch -M main

git push -u *rigin main
```

---

# Workflow*
```text
08*00
Generate Content

08:05*Generate Caption

08:06*Generate Image

08:08
Save Databas**
08:10
Schedule Post

13*00
Auto Publish

20:00
*uto*Publish
```

---

# Security*Best*Practices

- Jangan commit file `.*nv`
- Jangan simpan password di so*rce code
* Aktifkan Instagram 2FA
-*Backup PostgreSQL secara berkala
-*Gunakan session*login Playwright
- Monitoring*log*posting setiap hari
- Gunakan appr*val workflow sebelum publish*otomatis*untuk mengurangi risiko konten yan* tidak sesuai
````*


                    +------------------+
                    | Django Admin     |
                    | Dashboard        |
                    +--------+---------+
                             |
                             v
+------------+      +------------------+
| Celery Beat| ---> | Celery Worker    |
+------------+      +--------+---------+
                             |
             +---------------+---------------+
             |                               |
             v                               v
+----------------------+      +----------------------+
| AI Content Generator |      | Image Generator      |
| Caption              |      | DALL-E / SD / Flux   |
| Hashtag              |      |                      |
+----------+-----------+      +----------+-----------+
           |                             |
           +-------------+---------------+
                         |
                         v
                +------------------+
                | PostgreSQL       |
                | Post Storage     |
                +---------+--------+
                          |
                          v
                +------------------+
                | Redis Cache      |
                +---------+--------+
                          |
                          v
                +------------------+
                | Publishing Queue |
                +---------+--------+
                          |
                          v
                +------------------+
                | Instagram Bot    |
                | Playwright       |
                +------------------+


                Post Topic
# AI Image Generator Service

Modul ini bertanggung jawab untuk membuat gambar Instagram secara otomatis menggunakan AI Image Generation API yang kompatibel dengan OpenAI Image Endpoint.

---

# Tujuan

Service ini digunakan untuk:

- Generate gambar Instagram otomatis
- Generate gambar berdasarkan topik
- Generate thumbnail viral
- Generate ilustrasi berita
- Generate desain sosial media
- Menyimpan hasil gambar ke Django Media Storage
- Integrasi dengan Celery
- Integrasi dengan PostgreSQL

---

# Flow

```text
Topic
  |
  V
Generate Prompt
  |
  V
AI Image Generator
  |
  V
Download Image
  |
  V
Save Media File
  |
  V
Save Database