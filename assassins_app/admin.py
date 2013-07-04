from django.contrib import admin
from assassins_app.models import Game, Player
from random import shuffle


def delete_all_players(model_admin, request, queryset):
  pass


def reset_players(model_admin, request, queryset):
  for game in queryset:
    players = Player.objects.filter(game = game)
    for player in players:
      player.target_number = ''
      player.waiting_response = ''
      player.is_alive = True
      player.kill_count = 0
      player.save()


def assign_targets(model_admin, request, queryset):
  for game in queryset:
    players = Player.objects.filter(game = game)
    player_numbers = [player.phone_number for player in players]
    shuffle(player_numbers)
    for player in players:
      player.target_number = player_numbers.pop()
      player.save()


class GameAdmin(admin.ModelAdmin):
  actions = [delete_all_players,
             reset_players,
             assign_targets]


admin.site.register(Game, GameAdmin)
admin.site.register(Player)