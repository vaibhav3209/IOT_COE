from django.apps import AppConfig

# ========================
# - Register your app here every time
#     we create it from django

# - Also write it in settings.py-> Installed_apps
# ========================

class FinalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'final'
