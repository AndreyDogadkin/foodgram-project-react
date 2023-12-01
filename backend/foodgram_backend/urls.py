from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('api/', include('api.urls')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    import debug_toolbar  # TODO УДАЛИТЬ

    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    urlpatterns += [
        path(r'^__debug__/', include(debug_toolbar.urls)),  # TODO УДАЛИТЬ
    ]
