from django.conf import settings
from django.contrib import admin
from django.urls import path, include


# ========================
# 1. All paths are inside `Final` app's directory
# 2. Admin path is intentionally configurable for security reasons
# ========================
urlpatterns = [
    path(settings.ADMIN_PATH, admin.site.urls),
    path('',include('final.urls')),
    path('', include('simulation.urls'))
]
