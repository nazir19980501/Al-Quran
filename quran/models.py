from django.conf import settings
from django.db import models

class Surah(models.Model):
    number = models.PositiveSmallIntegerField(unique=True)
    name_arabic = models.CharField(max_length=120)
    name_english = models.CharField(max_length=120)
    english_meaning = models.CharField(max_length=160, blank=True)
    revelation_type = models.CharField(max_length=20, blank=True)
    total_verses = models.PositiveSmallIntegerField(default=0)
    class Meta:
        ordering = ["number"]
    def __str__(self):
        return f"{self.number}. {self.name_english}"

class Ayah(models.Model):
    surah = models.ForeignKey(Surah, on_delete=models.CASCADE, related_name="ayahs")
    verse_number = models.PositiveSmallIntegerField()
    global_number = models.PositiveIntegerField(unique=True, db_index=True)
    arabic_text = models.TextField()
    juz_number = models.PositiveSmallIntegerField(null=True, blank=True, db_index=True)
    hizb_number = models.PositiveSmallIntegerField(null=True, blank=True, db_index=True)
    page_number = models.PositiveSmallIntegerField(null=True, blank=True, db_index=True)
    class Meta:
        ordering = ["surah__number", "verse_number"]
        constraints = [models.UniqueConstraint(fields=["surah", "verse_number"], name="unique_ayah_in_surah")]
    def __str__(self):
        return f"{self.surah.number}:{self.verse_number}"

class Language(models.Model):
    code = models.CharField(max_length=12, unique=True)
    name = models.CharField(max_length=80)
    native_name = models.CharField(max_length=80, blank=True)
    is_rtl = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    class Meta:
        ordering = ["name"]
    def __str__(self):
        return self.name

class TranslationEdition(models.Model):
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name="editions")
    identifier = models.CharField(max_length=100, unique=True)
    translator = models.CharField(max_length=180, blank=True)
    source = models.CharField(max_length=120, default="AlQuran Cloud")
    attribution = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.language.name}: {self.translator or self.identifier}"

class AyahTranslation(models.Model):
    ayah = models.ForeignKey(Ayah, on_delete=models.CASCADE, related_name="translations")
    edition = models.ForeignKey(TranslationEdition, on_delete=models.CASCADE, related_name="ayah_translations")
    text = models.TextField()
    class Meta:
        constraints = [models.UniqueConstraint(fields=["ayah", "edition"], name="unique_ayah_translation")]
    def __str__(self):
        return f"{self.ayah} / {self.edition}"

class Bookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="quran_bookmarks")
    ayah = models.ForeignKey(Ayah, on_delete=models.CASCADE, related_name="bookmarks")
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["-created_at"]
        constraints = [models.UniqueConstraint(fields=["user", "ayah"], name="unique_user_ayah_bookmark")]
    def __str__(self):
        return f"{self.user} → {self.ayah}"
