# BeYou

BeYou is a Django e-commerce project with account login, product browsing, cart management, checkout, order tracking, and profile image uploads.

## Requirements

- Python 3.12+
- pip

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and fill in your real values:

```env
DJANGO_SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
DEFAULT_FROM_EMAIL=webmaster@example.com
```

4. Run migrations:

```bash
python manage.py migrate
```

5. Start the server:

```bash
python manage.py runserver
```

## GitHub Safety

Do not upload these local files:

- `.env`
- `db.sqlite3`
- `media/`
- `aenv/`
- `__pycache__/`

The included `.gitignore` excludes them.
