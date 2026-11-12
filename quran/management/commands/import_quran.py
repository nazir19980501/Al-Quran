import requests
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from quran.models import Surah, Ayah, Language, TranslationEdition, AyahTranslation

API = "https://api.alquran.cloud/v1"
LANGUAGES = {
    "en": ("English", "English", False),
    "fa": ("Persian (verify Dari suitability)", "فارسی", True),
    "ur": ("Urdu", "اردو", True),
    "ps": ("Pashto", "پښتو", True),
    "tr": ("Turkish", "Türkçe", False),
    "fr": ("French", "Français", False),
    "id": ("Indonesian", "Bahasa Indonesia", False),
    "de": ("German", "Deutsch", False),
}

class Command(BaseCommand):
    help = "Import Uthmani Arabic Quran, section metadata, and available translations."

    def add_arguments(self, parser):
        parser.add_argument("--languages", default="en,fa,ur,ps,tr,fr,id,de")
        parser.add_argument("--arabic-only", action="store_true")

    def get_json(self, path):
        try:
            response = requests.get(f"{API}/{path}", timeout=60)
            response.raise_for_status()
            payload = response.json()
            if payload.get("code") != 200:
                raise CommandError(f"API error for {path}: {payload}")
            return payload["data"]
        except requests.RequestException as exc:
            raise CommandError(f"Could not download {path}: {exc}")

    @transaction.atomic
    def handle(self, *args, **opts):
        self.stdout.write("Downloading Uthmani Arabic text and Juz/Hizb/page metadata...")
        arabic = self.get_json("quran/quran-uthmani")
        for item in arabic["surahs"]:
            surah, _ = Surah.objects.update_or_create(
                number=item["number"],
                defaults={
                    "name_arabic": item["name"],
                    "name_english": item.get("englishName", item["name"]),
                    "english_meaning": item.get("englishNameTranslation", ""),
                    "revelation_type": item.get("revelationType", ""),
                    "total_verses": len(item["ayahs"]),
                },
            )
            for verse in item["ayahs"]:
                quarter = verse.get("hizbQuarter")
                Ayah.objects.update_or_create(
                    global_number=verse["number"],
                    defaults={
                        "surah": surah,
                        "verse_number": verse["numberInSurah"],
                        "arabic_text": verse["text"],
                        "juz_number": verse.get("juz"),
                        "hizb_number": ((quarter + 3) // 4) if quarter else None,
                        "page_number": verse.get("page"),
                    },
                )
        self.stdout.write(self.style.SUCCESS(
            f"Imported {Surah.objects.count()} Surahs and {Ayah.objects.count()} Ayahs."
        ))
        if opts["arabic_only"]:
            return

        for code in [x.strip().lower() for x in opts["languages"].split(",") if x.strip()]:
            if code not in LANGUAGES:
                self.stdout.write(self.style.WARNING(f"Skipping unsupported language code: {code}"))
                continue
            name, native, rtl = LANGUAGES[code]
            self.stdout.write(f"Looking for an available {name} translation...")
            editions = self.get_json(f"edition?format=text&type=translation&language={code}")
            if not editions:
                self.stdout.write(self.style.WARNING(f"No translation editions found for {code}; skipped."))
                continue
            edition_data = editions[0]
            identifier = edition_data["identifier"]
            language, _ = Language.objects.update_or_create(
                code=code,
                defaults={"name": name, "native_name": native, "is_rtl": rtl, "is_active": True},
            )
            edition, _ = TranslationEdition.objects.update_or_create(
                identifier=identifier,
                defaults={
                    "language": language,
                    "translator": edition_data.get("englishName", edition_data.get("name", identifier)),
                    "source": "AlQuran Cloud",
                    "attribution": "Verify the translation's licence and attribution terms before public redistribution.",
                    "is_default": True,
                },
            )
            translated = self.get_json(f"quran/{identifier}")
            count = 0
            for surah_data in translated["surahs"]:
                for verse in surah_data["ayahs"]:
                    ayah = Ayah.objects.filter(global_number=verse["number"]).first()
                    if ayah:
                        AyahTranslation.objects.update_or_create(
                            ayah=ayah, edition=edition, defaults={"text": verse["text"]}
                        )
                        count += 1
            self.stdout.write(self.style.SUCCESS(f"{identifier}: imported {count} translation verses."))
        self.stdout.write(self.style.SUCCESS(
            "Import complete. Verify translation attribution/licences and confirm Persian vs Dari wording."
        ))
