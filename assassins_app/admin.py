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

  model_admin.message_user(
    request,
    "Reset players in %d game(s)." % len(queryset))


def assign_targets(model_admin, request, queryset):
  for game in queryset:
    # generate target list
    players = Player.objects.filter(game=game).order_by('phone_number')
    indices = range(len(players))
    shuffle(indices)

    # Each player gets as a target the player following him/her in the list.
    for i, player_index in enumerate(indices, start=1):
      if i < len(indices):
        target = players[indices[i]]
      else:
        target = players[indices[0]]
      players[player_index].target_number = target.phone_number
      players[player_index].save()

  model_admin.message_user(
      request,
      "Successfully assigned targets for %d game(s)." % len(queryset))


def send_initial_targets(model_admin, request, queryset):
  num_players = 0
  for game in queryset:
    players = Player.objects.filter(game = game)
    num_players += len(players)
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

  model_admin.message_user(
      request,
      "Sent initial target to %d user(s) in %d game(s)." % 
      (num_players, len(queryset)))


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


class PlayerAdmin(admin.ModelAdmin):
  list_display = ('__unicode__', 'game', 'phone_number', 'ldap', 'alias', 'target_number')
  list_filter = ('game', 'is_alive')


admin.site.register(Game, GameAdmin)
admin.site.register(Player, PlayerAdmin)
