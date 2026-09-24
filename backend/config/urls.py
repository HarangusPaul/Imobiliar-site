"""Root URL configuration.

Two surfaces only:

* ``/admin/``  - Django Admin, the internal CRUD fallback until the React
  dashboard exists. It is a stopgap, not the product.
* ``/api/v1/`` - the versioned API consumed by the Next.js frontend.
"""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Imobiliar - internal administration"
admin.site.site_title = "Imobiliar admin"
admin.site.index_title = "Internal data management"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include(("config.api.v1", "api-v1"), namespace="v1")),
]

if settings.DEBUG:
    from django.conf.urls.static import static

    # Serves files written by services.storage.local during development only.
    urlpatterns += static(settings.LOCAL_STORAGE_BASE_URL, document_root=settings.LOCAL_STORAGE_ROOT)
