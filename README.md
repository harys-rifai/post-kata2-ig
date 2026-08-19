# Instagram AI Auto Post

Sistem otomatis untuk membuat dan mempublikasikan konten Instagram menggunakan AI untuk akun @jakarta24viral.

## Cara Kerja Aplikasi

Aplikasi ini bekerja dalam 3 tahap utama:

### 1. Generate Konten dengan AI

- Memilih topik secara acak atau berdasarkan input user (contoh: "Kata Kata Motivasi", "Wisata Jakarta", "AI", dll)
- Mengirim prompt ke **AI Router** (`http://localhost:20128/v1`) untuk menghasilkan:
  - **Title** - Judul singkat
  - **Caption** - Quote/motto dalam Bahasa Indonesia
  - **Hashtags** - 15 hashtag relevan
  - **Category** - Kategori konten: `hidup`, `ai`, atau `astrology`
- Menyimpan hasil ke database PostgreSQL dengan status `generated`

### 2. Generate Gambar

Setiap konten dilengkapi gambar otomatis:

- **Primary**: Memanggil AI Image Model (`tokenrouter/google/gemini-2.5-flash-image`) melalui AI Router untuk menghasilkan gambar sesuai `image_prompt`
- **Fallback**: Jika AI image tidak tersedia atau gagal, sistem otomatis membuat **placeholder image** lokal menggunakan Pillow (PIL):
  - Ukuran 1024x1024 PNG
  - Gradient background sesuai kategori:
    - `hidup` - Gradasi merah/pink dengan label "LIFE QUOTES"
    - `ai` - Gradasi ungu/cyan dengan label "AI INSIGHT"
    - `astrology` - Gradasi ungu tua/emas dengan dekorasi bintang dan label "COSMIC WISDOM"
  - Teks quote yang di-wrap otomatis dengan shadow untuk readability
  - Dekorasi acak: lingkaran transparan, bintang (astrology), atau circuit dots (ai)
- Gambar diproses dan di-resize menjadi maksimal 1024x1024 sebelum disimpan ke `media/`

### 3. Auto Publish ke Instagram

- **Celery Beat** menjadwalkan publish otomatis 3x sehari: **08:00**, **13:00**, **20:00**
- **Celery Worker** mengambil post dengan status `scheduled` yang waktunya sudah tiba
- Menggunakan **Playwright (Chromium headless)** untuk:
  - Login ke Instagram dengan session persistence (`storage/instagram_session.json`)
  - Upload gambar dari `media/`
  - Isi caption: `title + caption + hashtags`
  - Klik tombol Share
- Jika berhasil: status menjadi `published`
- Jika gagal: status menjadi `failed` dan `retry_count` bertambah
- **Auto Retry**: Celery Beat juga menjadwalkan retry failed posts setiap hari **06:00** dengan exponential backoff (2^retry_count menit)

## Alur Lengkap

```text
Celery Beat (07:30)
      │
      ▼
Generate Daily Content
- Pilih 10 topik acak
- AI Router generate title/caption/hashtags
- Generate image (AI atau placeholder)
- Simpan ke PostgreSQL (status: generated)
      │
      ▼
User Approval (opsional)
- User approve -> scheduled
- User reject -> draft
      │
      ▼
Celery Beat (08:00 / 13:00 / 20:00)
      │
      ▼
Auto Publish
- Playwright login Instagram
- Upload image + caption + hashtags
- Status: published / failed
      │
      ▼
Celery Beat (06:00 retry)
- Retry failed posts max 10x
- Exponential backoff
```

## Tech Stack

- **Backend**: Django 5.0
- **Database**: PostgreSQL
- **Cache & Queue**: Redis + Celery + Celery Beat
- **AI**: OpenAI-compatible API via AI Router (`http://localhost:20128/v1`)
- **Automation**: Playwright (Chromium headless)
- **Image Processing**: Pillow (PIL)

## Prerequisites

- Python 3.10+
- PostgreSQL (port 5008)
- Redis (port 6379)
- AI Router running at `http://localhost:20128/v1`
- Playwright Chromium browser

## Instalasi

1. Clone repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install Playwright browser:
   ```bash
   playwright install chromium
   ```
4. Configure environment variables di `.env`
5. Buat database PostgreSQL `instagram_ai`
6. Jalankan migrasi:
   ```bash
   python manage.py migrate
   ```
7. Buat superuser:
   ```bash
   python manage.py createsuperuser
   ```

## Menjalankan Aplikasi

### Windows (run.bat)
```bash
run.bat
```

`run.bat` akan otomatis:
- Membunuh proses lama
- Menyalakan Redis dari `C:\redis\redis-server.exe`
- Menjalankan Celery Worker, Celery Beat, dan Django server di port 809

### Manual
```bash
# Terminal 1 - Redis
redis-server

# Terminal 2 - Celery Worker
celery -A config worker -l info

# Terminal 3 - Celery Beat
celery -A config beat -l info

# Terminal 4 - Django
python manage.py runserver 809
```

## Akses

- App: `http://127.0.0.1:809/`
- Admin: `http://127.0.0.1:809/admin/`
- Login: `http://127.0.0.1:809/login/`

## Environment Variables

| Variable | Deskripsi | Default |
|----------|-----------|---------|
| `DEBUG` | Django debug mode | `True` |
| `SECRET_KEY` | Django secret key | - |
| `DB_NAME` | Nama database PostgreSQL | `instagram_ai` |
| `DB_USER` | Username PostgreSQL | `postgres` |
| `DB_PASSWORD` | Password PostgreSQL | - |
| `DB_HOST` | Host PostgreSQL | `localhost` |
| `DB_PORT` | Port PostgreSQL | `5008` |
| `REDIS_URL` | Redis connection URL | `redis://:Password09!@localhost:6379/0` |
| `AI_API_BASE` | AI Router base URL | `http://localhost:20128/v1` |
| `AI_API_KEY` | AI API key | - |
| `AI_MODEL` | AI model untuk text | `kc/kilo-auto/free` |
| `AI_IMAGE_MODEL` | AI model untuk gambar | `tokenrouter/google/gemini-2.5-flash-image` |
| `INSTAGRAM_USERNAME` | Instagram username | - |
| `INSTAGRAM_PASSWORD` | Instagram password | - |

## Celery Beat Schedule

| Task | Jadwal | Deskripsi |
|------|--------|-----------|
| `generate_morning_content` | 07:30 | Generate 10 konten harian |
| `retry_failed_posts` | 06:00 | Retry post yang gagal |
| `morning_post` | 08:00 | Publish scheduled posts |
| `afternoon_post` | 13:00 | Publish scheduled posts |
| `night_post` | 20:00 | Publish scheduled posts |

## Kategori Konten

Aplikasi membuat konten dalam 3 kategori:

| Kategori | Topik | Tema Gambar |
|----------|-------|-------------|
| `hidup` | Motivasi, kehidupan, cinta, persahabatan | Gradasi merah/pink |
| `ai` | Teknologi, AI, robot, machine learning | Gradasi ungu/cyan |
| `astrology` | Zodiak, horoscope, bintang, ramalan | Gradasi ungu tua/emas + bintang |

## Struktur Project

```
post-ig/
├── config/
│   ├── settings.py          # Django settings + Celery config
│   ├── urls.py              # URL routing
│   ├── celery.py            # Celery app + Beat schedule
│   └── views.py             # Semua views (dashboard, generate, schedule, monitoring)
├── posts/
│   ├── models.py            # Post, InstagramConnection, Topic
│   ├── services.py          # PostService + InstagramConnectionService
│   ├── tasks.py             # Celery tasks: generate, auto_publish, retry
│   └── migrations/          # Database migrations
├── ai/
│   └── services.py          # AIService + InstagramAutomationService
├── scheduler/
│   └── tasks.py             # Daily content generation (10 topik)
├── templates/
│   ├── base.html            # Layout utama
│   ├── dashboard.html       # Statistik
│   ├── generate.html        # Generate konten AI
│   ├── settings.html        # Config + test IG connection
│   ├── approval.html        # Approval workflow
│   ├── schedule.html        # Scheduled + failed posts
│   └── monitoring.html      # Monitoring dashboard
├── media/                   # Uploaded images
├── logs/                    # Log files
├── storage/
│   └── instagram_session.json # Session persistence Instagram
└── run.bat                  # Startup script
```

## Catatan

- AI Router harus berjalan di `http://localhost:20128/v1`
- Playwright Chromium harus terinstall
- Redis harus berjalan untuk Celery worker dan beat
- Session Instagram disimpan di `storage/instagram_session.json`
- Jika AI Image tidak tersedia, sistem fallback ke placeholder image yang di-generate lokal
