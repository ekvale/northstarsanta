from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('pages.urls')),
    path('admin/', admin.site.urls),
    path("tinymce/", include("tinymce.urls")),
    path("posts/", include("blog.urls"))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
