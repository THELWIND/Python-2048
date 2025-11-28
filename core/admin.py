from django.contrib import admin
from .models import GameScore

@admin.register(GameScore)
class GameScoreAdmin(admin.ModelAdmin):
    list_display = ('user', 'score', 'game_mode', 'duration_seconds', 'created_at')
    list_filter = ('created_at', 'game_mode')
    search_fields = ('user__username',)