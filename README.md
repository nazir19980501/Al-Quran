# Al-Quran — Django Quran Reader

Responsive Django Quran website with Uthmani Arabic text, translations, daily Ayah, search, personal bookmarks, Juz/Hizb/page navigation, and an audio recitation player.

## Features
- Browse all 114 Surahs and read Arabic Quran text with translation editions
- Daily Ayah selected consistently by local date
- Search Arabic and selected translation
- Registration, login, and personal bookmarks
- Audio player: multiple reciters, individual Ayah, full Surah, previous/next verse
- Juz (30), Hizb (60), and Madani Mushaf page (604) metadata and navigation
- Django admin for Quran content, translations, and languages
- Responsive layout and custom SVG favicon
- SQLite by default; optional PostgreSQL

## Windows setup
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Open http://127.0.0.1:8000/

## Quran data
The existing database is intentionally retained. Run the importer to refresh Uthmani Arabic text and populate Juz, Hizb, and page metadata:
```powershell
python manage.py migrate
python manage.py import_quran
```
Arabic only: `python manage.py import_quran --arabic-only`
Choose languages: `python manage.py import_quran --languages en,fa,ur,ps,tr,fr,id,de`

AlQuran Cloud is used as an import source. API availability does not itself grant permission to redistribute every translation. Verify the translator, attribution, and licence terms before publication. Persian (fa) is not automatically Dari; verify the edition before labelling it Dari.

## Audio
Audio is delivered by the Islamic Network CDN. The player includes Alafasy, Sudais, Husary, Minshawi, and Maher Al-Muaiqly. Internet access is required. Confirm current provider availability and terms before production use.

## Production checklist
Set a strong DJANGO_SECRET_KEY, DEBUG=False, and ALLOWED_HOSTS; use HTTPS, secure cookies, database backups, and PostgreSQL for a production deployment. Verify Quran text and translation data before public launch. The SQLite database is intentionally preserved in Git because it contains the Quran dataset.
