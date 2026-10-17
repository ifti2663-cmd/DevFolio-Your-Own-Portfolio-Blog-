# DevFolio API

A Django REST Framework API for a single-owner developer portfolio and blog. Post content is stored as Markdown and rendered safely by the React client.

## Stack

Django, Django REST Framework, Simple JWT with refresh-token blacklisting, django-filter, django-cors-headers, Pillow, SQLite, and python-decouple.

## Setup

```bash
cd backend
python -m venv venv
# Activate venv, then:
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Create the one initial `Profile` in Django admin at `/admin/`; after that it can be maintained from the dashboard. Add real portfolio content only: at least 10 skills, 3 projects, 5 posts (4 published and one draft), 3 categories, 6 tags, comments, and contact messages as specified in the brief.

## Environment

| Variable | Purpose |
| --- | --- |
| `SECRET_KEY` | Django secret key |
| `DEBUG` | `True` only for local development |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts |
| `CORS_ALLOWED_ORIGINS` | Comma-separated frontend origins |
| `DB_ENGINE`, `DB_NAME` | Database configuration |

## API overview

| Resource | Public read | Owner write |
| --- | --- | --- |
| `/api/profile/` | GET | PATCH |
| `/api/skills/`, `/api/experiences/`, `/api/education/` | GET | POST/PATCH/DELETE |
| `/api/projects/`, `/api/projects/:slug/` | GET | POST/PATCH/DELETE |
| `/api/posts/`, `/api/posts/:slug/` | Published only | POST/PATCH/DELETE incl. drafts |
| `/api/posts/:slug/like/`, `/comments/` | POST/GET | — |
| `/api/categories/`, `/api/tags/` | GET | POST/PATCH/DELETE |
| `/api/contact/` | POST | GET/PATCH/DELETE |
| `/api/comments/`, `/api/dashboard/stats/` | — | GET/PATCH/DELETE |

Authentication is available at `/api/auth/login/`, `/refresh/`, `/logout/`, `/me/`, and `/change-password/`. There is intentionally no registration endpoint.

## Security and behaviour

`IsOwnerOrReadOnly` allows safe requests for everyone and requires both an authenticated JWT and `is_superuser` for every write. Published posts only are exposed publicly. Comments are unapproved by default and public serializers never return their email addresses.

The frontend persists a UUID and sends it as `X-Visitor-Id`. A `PostView` row records its last counted view, so the server increments with `F()` only on a new visitor or after a one-hour cooldown. Likes are unique by post and visitor UUID.

Rates: anonymous traffic 20/min, comments 5/hour/IP, contact submissions 3/hour/IP, and likes 30/min. The response-time middleware adds `X-Response-Time`; the comment signal emits a console-email notification for pending comments.

See `postman_collection.json` for a runnable collection. Frontend repository: `../frontend` (replace this with the public repository URL before submission).
