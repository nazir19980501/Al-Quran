from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from quran import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("surahs/", views.surah_list, name="surah_list"),
    path("surah/<int:number>/", views.reader, name="reader"),
    path("browse/<str:kind>/<int:number>/", views.browse_section, name="browse_section"),
    path("search/", views.search, name="search"),
    path("bookmarks/", views.bookmarks, name="bookmarks"),
    path("bookmark/<int:ayah_id>/", views.toggle_bookmark, name="toggle_bookmark"),
    path("accounts/login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("accounts/register/", views.register, name="register"),
]
