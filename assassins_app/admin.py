from django.contrib import admin
from django.shortcuts import render_to_response
from django.template import RequestContext
from assassins_app.models import Game, Player
from random import shuffle
import requests
from django import forms


class DeleteAllPlayersForm(forms.Form):
  _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)


def delete_all_players(model_admin, request, queryset):
  form = None

  if 'cancel' in request.POST:
    # user clicked cancel
    model_admin.message_user(request, 'Action canceled.')
    return

  if 'apply' in request.POST and request.POST['action'] == 'delete_all_players':
    # message form submitted; validate
    form = DeleteAllPlayersForm(request.POST)
    for game in queryset:
      players = Player.objects.filter(game = game).delete()
    model_admin.message_user(request, "Deleted all players.")
    return
  
  if not form:
    # we have either never displayed the form
    form = DeleteAllPlayersForm(
        initial={'_selected_action':
        request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})
  
  return render_to_response('admin/delete_all_players.html',
                            {
                              'games': queryset,
                              'form': form,
                            },
                            context_instance = RequestContext(request))


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
  def is_derangement(old_list, new_list):
    for i in range(len(old_list)):
      if old_list[i] == new_list[i]:
        return False
    return True

  def is_cyclic(players, targets):
    unique_players = set()
    current_player = 0
    for hop in range(len(players)):
      unique_players.add(players[current_player])
      current_player = players.index(targets[current_player])
    return True if len(unique_players) == len(players) else False


  for game in queryset:
    # generate target list
    players = Player.objects.filter(game = game).order_by('phone_number')
    player_numbers = [player.phone_number for player in players]
    shuffled_numbers = player_numbers[:] # make a copy
    while not (is_derangement(player_numbers, shuffled_numbers) and
        is_cyclic(player_numbers, shuffled_numbers)):
      shuffle(shuffled_numbers)

    # assign targets to players
    for player in players:
      player.target_number = shuffled_numbers.pop(0)
      player.save()

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


class SendMassMessageForm(forms.Form):
  _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
  message = forms.CharField(max_length = 160,
                            required = True)


def send_mass_message(model_admin, request, queryset):
  form = None

  if 'cancel' in request.POST:
    # user clicked cancel
    model_admin.message_user(request, 'Action canceled.')
    return

  if 'apply' in request.POST and request.POST['action'] == 'send_mass_message':
    # message form submitted; validate
    form = SendMassMessageForm(request.POST)
    if form.is_valid():
      message = form.cleaned_data['message']
      for game in queryset:
        players = Player.objects.filter(game = game)
        for player in players:
          _sendNewMessage(message, player.phone_number, game.token)
      model_admin.message_user(request, "Sent mass message.")
      return
    else:
      model_admin.message_user(request, "Message was not valid.")
  
  if not form:
    # we have either never displayed the form
    form = SendMassMessageForm(
        initial={'_selected_action':
        request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})
  
  return render_to_response('admin/send_mass_message.html',
                            {
                              'games': queryset,
                              'form': form,
                            },
                            context_instance = RequestContext(request))



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
             send_initial_targets,
             send_mass_message]


admin.site.register(Game, GameAdmin)
admin.site.register(Player)
