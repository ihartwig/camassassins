from django.contrib import admin
from assassins_app.models import Game, Player
from random import shuffle
import requests


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
    # TODO: make sure we didn't assign themselves
    players = Player.objects.filter(game = game)
    player_numbers = [player.phone_number for player in players]
    shuffle(player_numbers)
    for player in players:
      player.target_number = player_numbers.pop()
      player.save()


def send_initial_targets(model_admin, request, queryset):
  for game in queryset:
    players = Player.objects.filter(game = game)
    for player in players:
      try:
        target = Player.objects.get(game = game,
                                    phone_number = player.target_number)
      except Player.DoesNotExist:
        _sendNewMessage('Couldn\'t find your initial target. Contact game admin.',
                        player.phone_number,
                        game.token)
      
      _sendNewMessage('Your initial target is ' + target.ldap + '@google.com.',
                      player.phone_number,
                      game.token)


def _sendNewMessage(msg, to, token):
  payload = {
    'action': 'create',
    'token': token,
    'outboundmsg': msg,
    'outboundnum': to,
  }
  url = 'https://api.tropo.com/1.0/sessions'
  r = requests.get(url, params = payload)
  if(r.status_code == 200):
    return True
  else:
    return False


class GameAdmin(admin.ModelAdmin):
  actions = [delete_all_players,
             reset_players,
             assign_targets,
             send_initial_targets]


admin.site.register(Game, GameAdmin)
admin.site.register(Player)