from django.contrib import admin
from .models import Surah, Ayah, Language, TranslationEdition, AyahTranslation, Bookmark

class AyahInline(admin.TabularInline):
    model = Ayah
    extra = 0
    fields = ("verse_number", "global_number", "arabic_text")
    show_change_link = True

@admin.register(Surah)
class SurahAdmin(admin.ModelAdmin):
    list_display = ("number", "name_english", "name_arabic", "total_verses", "revelation_type")
    search_fields = ("name_english", "name_arabic")
    inlines = [AyahInline]

@admin.register(Ayah)
class AyahAdmin(admin.ModelAdmin):
    list_display = ("global_number", "surah", "verse_number")
    search_fields = ("arabic_text",)
    list_filter = ("surah",)

admin.site.register(Language)
admin.site.register(TranslationEdition)
admin.site.register(AyahTranslation)
admin.site.register(Bookmark)
