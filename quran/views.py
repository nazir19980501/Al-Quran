from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .models import Surah, Ayah, Language, Bookmark

AUDIO_RECITERS = [
    ("ar.alafasy", "Mishary Rashid Alafasy"),
    ("ar.abdurrahmaansudais", "Abdurrahman Al-Sudais"),
    ("ar.husary", "Mahmoud Khalil Al-Husary"),
    ("ar.minshawi", "Mohamed Siddiq Al-Minshawi"),
    ("ar.mahermuaiqly", "Maher Al-Muaiqly"),
]

def selected_language(request):
    code = request.GET.get("lang") or request.session.get("quran_language", "en")
    language = Language.objects.filter(code=code, is_active=True).first()
    if language:
        request.session["quran_language"] = language.code
    return language or Language.objects.filter(is_active=True).first()

def common_context(request, language):
    return {
        "language": language,
        "languages": Language.objects.filter(is_active=True),
        "audio_reciters": AUDIO_RECITERS,
        "juz_numbers": range(1, 31),
        "hizb_numbers": range(1, 61),
        "page_numbers": range(1, 605),
    }

def home(request):
    language = selected_language(request)
    total = Ayah.objects.count()
    daily_ayah = None
    if total:
        index = (timezone.localdate().toordinal() - 1) % total
        daily_ayah = Ayah.objects.select_related("surah").order_by("global_number")[index]
    daily_translation = None
    if daily_ayah and language:
        daily_translation = daily_ayah.translations.filter(edition__language=language).select_related("edition").first()
    context = common_context(request, language)
    context.update({
        "daily_ayah": daily_ayah, "daily_translation": daily_translation,
        "surahs": Surah.objects.all()[:12], "total_ayahs": total,
    })
    return render(request, "quran/home.html", context)

def surah_list(request):
    language = selected_language(request)
    context = common_context(request, language)
    context["surahs"] = Surah.objects.all()
    return render(request, "quran/surah_list.html", context)

def reader(request, number):
    surah = get_object_or_404(Surah, number=number)
    language = selected_language(request)
    ayahs = list(surah.ayahs.prefetch_related("translations__edition__language"))
    saved_ids = set()
    if request.user.is_authenticated:
        saved_ids = set(Bookmark.objects.filter(user=request.user, ayah__surah=surah).values_list("ayah_id", flat=True))
    playlist = [{"global": a.global_number, "verse": a.verse_number, "surah": surah.number} for a in ayahs]
    context = common_context(request, language)
    context.update({"surah": surah, "ayahs": ayahs, "saved_ids": saved_ids, "audio_playlist": playlist})
    return render(request, "quran/reader.html", context)

def search(request):
    query = request.GET.get("q", "").strip()
    language = selected_language(request)
    results = []
    if query:
        lookup = Q(arabic_text__icontains=query)
        if language:
            lookup |= Q(translations__text__icontains=query, translations__edition__language=language)
        results = Ayah.objects.filter(lookup).select_related("surah").distinct()[:100]
    context = common_context(request, language)
    context.update({"query": query, "results": results})
    return render(request, "quran/search.html", context)

def browse_section(request, kind, number):
    fields = {"juz": "juz_number", "hizb": "hizb_number", "page": "page_number"}
    limits = {"juz": 30, "hizb": 60, "page": 604}
    if kind not in fields or number < 1 or number > limits[kind]:
        messages.error(request, "That Quran section number is not valid.")
        return redirect("home")
    ayah = Ayah.objects.filter(**{fields[kind]: number}).order_by("global_number").first()
    if not ayah:
        messages.warning(request, "Section metadata is not imported yet. Run the Quran import command again.")
        return redirect("home")
    return redirect(f"/surah/{ayah.surah.number}/?ayah={ayah.verse_number}#ayah-{ayah.id}")

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
    context = common_context(request, language)
    context["saved"] = saved
    return render(request, "quran/bookmarks.html", context)

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
