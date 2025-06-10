from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("blank_app/", include("blank_app.urls")),
    path("admin/", admin.site.urls),
]
