# Instagram AI Auto Post

Sistem otomatis untuk membuat dan mempublikasikan konten Instagram menggunakan AI.

## Fitur Utama

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

## Target Account

Instagram Account
@jakarta24viral

## System Architecture

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
Generate Hashtag
     │
     ▼
Generate Image Prompt
     │
     ▼
Generate Image
     │
     ▼
Save to PostgreSQL
     │
     ▼
Celery Worker
     │
     ▼
Publish to Instagram (Playwright)
     │
     ▼
Update Status
```

## Tech Stack

- **Backend**: Django 5.0
- **Database**: PostgreSQL
- **Cache**: Redis
- **Task Queue**: Celery + Celery Beat
- **AI**: OpenAI-compatible API via local AI Router
- **Automation**: Playwright (Chromium)
- **Image Processing**: Pillow

## Prerequisites

- Python 3.10+
- PostgreSQL (port 5008)
- Redis (port 6379)
- AI Router running at `http://localhost:20128/v1`
- Playwright Chromium browser

## Installation

1. Clone repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install Playwright browser:
   ```bash
   playwright install chromium
   ```
4. Configure environment variables in `.env`
5. Create PostgreSQL database `instagram_ai`
6. Run migrations:
   ```bash
   python manage.py migrate
   ```
7. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```

## Running the Application

### Using run.bat (Windows)

- `run.bat` will try to start Redis from `C:\redis\redis-server.exe` if it is not found in PATH.
- Make sure `C:\redis\redis.windows.conf` uses the same password as `REDIS_URL` in `.env`.
- If Redis is already running manually, `run.bat` will reuse it.

```bash
run.bat
```

### Manual Start

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

## Access Points

- Main App: `http://127.0.0.1:809/`
- Admin Panel: `http://127.0.0.1:809/admin/`
- Login: `http://127.0.0.1:809/login/`

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Django debug mode | `True` |
| `SECRET_KEY` | Django secret key | - |
| `DB_NAME` | PostgreSQL database name | `instagram_ai` |
| `DB_USER` | PostgreSQL username | `postgres` |
| `DB_PASSWORD` | PostgreSQL password | - |
| `DB_HOST` | PostgreSQL host | `localhost` |
| `DB_PORT` | PostgreSQL port | `5008` |
| `REDIS_URL` | Redis connection URL | `redis://:Password09!@localhost:6379/0` |
| `AI_API_BASE` | AI Router base URL | `http://localhost:20128/v1` |
| `AI_API_KEY` | AI API key | - |
| `AI_MODEL` | AI model name | `kc/kilo-auto/free` |
| `AI_IMAGE_MODEL` | AI image model | `tokenrouter/google/gemini-2.5-flash-image` |
| `INSTAGRAM_USERNAME` | Instagram username | - |
| `INSTAGRAM_PASSWORD` | Instagram password | - |

## Celery Beat Schedule

| Task | Schedule | Description |
|------|----------|-------------|
| `morning_post` | 08:00 | Auto publish scheduled posts |
| `afternoon_post` | 13:00 | Auto publish scheduled posts |
| `night_post` | 20:00 | Auto publish scheduled posts |
| `generate_morning_content` | 07:30 | Generate daily content |
| `retry_failed_posts` | 06:00 | Retry failed posts |

## Project Structure

```
post-ig/
├── config/
│   ├── settings.py          # Django settings
│   ├── urls.py              # URL routing
│   ├── wsgi.py              # WSGI application
│   ├── asgi.py              # ASGI application
│   ├── celery.py            # Celery app + Beat schedule
│   └── views.py             # All application views
├── posts/
│   ├── models.py            # Post + InstagramConnection + Topic models
│   ├── admin.py             # Admin configuration
│   ├── services.py          # PostService + InstagramConnectionService
│   ├── tasks.py             # Celery tasks
│   └── migrations/          # Database migrations
├── ai/
│   └── services.py          # AIService + InstagramAutomationService
├── scheduler/
│   └── tasks.py             # Daily content generation task
├── templates/
│   ├── base.html            # Unified sidebar layout
│   ├── login.html           # Login page
│   ├── dashboard.html       # Dashboard stats
│   ├── posts.html           # Posts list
│   ├── post_form.html       # Create/Edit post
│   ├── schedule.html        # Scheduled + Failed posts
│   ├── generate.html        # AI content generation
│   ├── settings.html        # Config + IG connection
│   ├── approval.html        # Approval workflow
│   └── monitoring.html      # Monitoring dashboard
├── storage/
│   └── instagram_session.json # Session persistence
├── media/                   # Uploaded images
├── logs/                    # Log files
├── manage.py
├── requirements.txt
├── .env
├── .gitignore
└── run.bat                  # Startup script
```

## Models

### Post
- `title` - Post title
- `topic` - Post topic/category
- `caption` - Instagram caption
- `hashtags` - Instagram hashtags
- `image_prompt` - AI image generation prompt
- `image` - Generated image (ImageField)
- `publish_at` - Scheduled publish datetime
- `status` - Post status (draft/generated/scheduled/posting/published/failed)
- `retry_count` - Number of retry attempts
- `error_message` - Last error message

### InstagramConnection
- `username` - Instagram username
- `status` - Connection status
- `last_login` - Last login timestamp
- `last_error` - Last error message
- `is_active` - Active connection flag

### Topic
- `name` - Topic name (unique)
- Used for content generation dropdown

## API Endpoints

### Web UI
- `/` - Dashboard
- `/login/` - Login page
- `/logout/` - Logout
- `/posts/` - Posts list
- `/posts/create/` - Create post
- `/posts/edit/<id>/` - Edit post
- `/posts/delete/<id>/` - Delete post
- `/schedule/` - Schedule list
- `/schedule/create/` - Schedule post
- `/schedule/delete/<id>/` - Unschedule post
- `/generate/` - Generate AI content
- `/approval/` - Approval workflow
- `/approval/approve/<id>/` - Approve post
- `/approval/reject/<id>/` - Reject post
- `/monitoring/` - Monitoring dashboard
- `/health/` - Health check endpoint
- `/admin/` - Django admin

## Logging

Log files are stored in `logs/` directory:
- `django.log` - Django application logs
- `celery.log` - Celery worker/beat logs

## Notes

- AI Router must be running at `http://localhost:20128/v1` for content generation
- Playwright Chromium must be installed for Instagram automation
- Redis must be running for Celery worker and beat
- On Windows, if `redis-server` is not in PATH, place Redis in `C:\redis` so `run.bat` can start it automatically
- Session persistence for Instagram is stored in `storage/instagram_session.json`
- The Redis password must match between `.env` (`REDIS_URL`) and `C:\redis\redis.windows.conf` (`requirepass`)

## Security

- Instagram credentials stored in `.env` file
- Session file should be protected from public access
- SECRET_KEY should be changed in production
- Database credentials should be secured
