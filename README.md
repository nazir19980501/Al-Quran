# Al-Quran — Django Quran Reader

A responsive Django starter project with Surah browsing, Arabic Quran text, translation editions, daily Ayah, user registration, and personal bookmarks.

## Included

- Responsive Tailwind-based layout for desktop, tablet, and mobile
- 114 Surah / Ayah database structure
- Arabic Uthmani text import
- Multiple translation editions and languages
- Language selector on the home page and reader
- Daily Ayah chosen deterministically from the date
- User registration, login, logout, and bookmarks
- Search in Arabic and the selected translation (database search)
- Django admin for managing Quran content and editions
- SQLite by default; optional PostgreSQL configuration

## 1. Requirements

- Python 3.10+
- Internet connection for the initial Quran data import
- PostgreSQL is optional; SQLite is easiest for development

## 2. Install on Windows

Open PowerShell in this folder:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py makemigrations quran
python manage.py migrate
python manage.py createsuperuser
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
venv\Scripts\Activate.ps1
```

## 3. Import Quran text and available translations

```powershell
python manage.py import_quran
```

The command imports the original Uthmani Arabic text and tries to find translation editions for English, Persian, Urdu, Pashto, Turkish, French, Indonesian, and German through AlQuran Cloud's edition catalogue.

You can choose languages:

```powershell
python manage.py import_quran --languages en,fa,ur,fr,tr
```

Arabic only:

```powershell
python manage.py import_quran --arabic-only
```

**Important:** API availability varies. A language may have no edition in the source catalogue, so it will be skipped. Persian (`fa`) is not automatically guaranteed to be a Dari translation. Before presenting it as Dari, verify the translator, vocabulary, source, and licence. Add a dedicated Dari edition only after confirming it is genuinely Dari.

The importer currently selects the first available translation edition for each language. Review each edition in Django admin and check its attribution and redistribution terms before publishing the site. API access and content terms can change.

## 4. Run the website

```powershell
python manage.py runserver
```

Open http://127.0.0.1:8000/

Admin: http://127.0.0.1:8000/admin/

## 5. PostgreSQL (optional)

Create a database, then update `.env`:

```env
DB_ENGINE=postgres
DB_NAME=quran_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=127.0.0.1
DB_PORT=5432
```

Set `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False`, and `DJANGO_ALLOWED_HOSTS` appropriately for production. Do not commit `.env` or expose secrets.

## Quran content and attribution

This starter uses AlQuran Cloud's public API as a data source. Review its current API terms and each individual translation's copyright/licence and attribution requirements. Public API availability does not itself grant permission to redistribute every translation. The original Arabic text is rendered as supplied and is marked `translate="no"` in the UI. Verify imported verse counts and content before launch.

For production-scale Quran content, consider Quran Foundation's official Content API. It requires server-side credentials and approved scopes; never place a client secret in frontend code. See:
- https://api-docs.quran.com/docs/quickstart/
- https://api-docs.quran.com/docs/api-reference/
- https://alquran.cloud/api

## Notes / next development steps

This is a working starter, not a fully audited production deployment. Before public launch:
- Verify all 6,236 ayahs and each imported translation against trusted editions.
- Review permissions, translator attribution, and licensing.
- Add pagination to the reader for performance on long Surahs.
- Improve search with PostgreSQL full-text search and Arabic normalization that does not alter displayed Quran text.
- Add audio recitation with an explicitly licensed audio source.
- Add automated tests, rate limiting, backups, HTTPS, secure cookies, and production static-file serving.
- Add dedicated Dari edition metadata instead of assuming Persian is Dari.
