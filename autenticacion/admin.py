from django.contrib import admin
from .models import Profile  # Asegúrate de importar tus modelos

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'token_app_session', 'first_session')
