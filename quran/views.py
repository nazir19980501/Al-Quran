from datetime import date
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from .models import Surah, Ayah, Language, Bookmark

def selected_language(request):
    code = request.GET.get("lang") or request.session.get("quran_language", "en")
    language = Language.objects.filter(code=code, is_active=True).first()
    if language:
        request.session["quran_language"] = language.code
    return language or Language.objects.filter(is_active=True).first()

def home(request):
    languages = Language.objects.filter(is_active=True)
    language = selected_language(request)
    total = Ayah.objects.count()
    daily_ayah = None
    if total:
        index = (date.today().toordinal() - 1) % total
        daily_ayah = Ayah.objects.select_related("surah").order_by("global_number")[index]
    daily_translation = None
    if daily_ayah and language:
        daily_translation = daily_ayah.translations.filter(edition__language=language).select_related("edition").first()
    surahs = Surah.objects.all()[:12]
    saved_ids = set()
    if request.user.is_authenticated:
        saved_ids = set(Bookmark.objects.filter(user=request.user).values_list("ayah_id", flat=True))
    return render(request, "quran/home.html", {
        "daily_ayah": daily_ayah, "daily_translation": daily_translation,
        "language": language, "languages": languages, "surahs": surahs,
        "saved_ids": saved_ids, "total_ayahs": total,
    })

def surah_list(request):
    language = selected_language(request)
    return render(request, "quran/surah_list.html", {
        "surahs": Surah.objects.all(), "languages": Language.objects.filter(is_active=True),
        "language": language,
    })

def reader(request, number):
    surah = get_object_or_404(Surah, number=number)
    language = selected_language(request)
    ayahs = surah.ayahs.prefetch_related("translations__edition__language")
    saved_ids = set()
    if request.user.is_authenticated:
        saved_ids = set(Bookmark.objects.filter(user=request.user, ayah__surah=surah).values_list("ayah_id", flat=True))
    return render(request, "quran/reader.html", {
        "surah": surah, "ayahs": ayahs, "language": language,
        "languages": Language.objects.filter(is_active=True), "saved_ids": saved_ids,
    })

def search(request):
    query = request.GET.get("q", "").strip()
    language = selected_language(request)
    results = []
    if query:
        results = Ayah.objects.filter(
            Q(arabic_text__icontains=query) |
            Q(translations__text__icontains=query, translations__edition__language=language)
        ).select_related("surah").distinct()[:80]
    return render(request, "quran/search.html", {
        "query": query, "results": results, "language": language,
        "languages": Language.objects.filter(is_active=True),
    })

@login_required
def toggle_bookmark(request, ayah_id):
    if request.method != "POST":
        return redirect("home")
    ayah = get_object_or_404(Ayah, pk=ayah_id)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, ayah=ayah)
    if not created:
        bookmark.delete()
        messages.info(request, "Bookmark removed.")
    else:
        messages.success(request, "Verse saved to your bookmarks.")
    return redirect(request.POST.get("next") or "home")

@login_required
def bookmarks(request):
    language = selected_language(request)
    saved = Bookmark.objects.filter(user=request.user).select_related("ayah__surah").prefetch_related("ayah__translations__edition__language")
    return render(request, "quran/bookmarks.html", {
        "saved": saved, "language": language,
        "languages": Language.objects.filter(is_active=True),
    })

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {"form": form})
