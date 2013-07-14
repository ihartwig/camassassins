from assassins_app.models import Game, Player, Activity
from django import http
from django.core import serializers
from django.db import DatabaseError, IntegrityError
from django.views.decorators.csrf import csrf_exempt
from django.utils import simplejson
from django.core import serializers
import re
import requests
from tropo import Tropo, Session, Say
import random

ADMIN_LDAP = 'vionalam'
ADMIN_MESSAGE = 'Please contact the game admin at who/'+ADMIN_LDAP
INCORRECT_CODE_LIMIT = 5

def activityFeed(request):
  if ('gamenumber' not in request.GET):
    print('no game number')
    return http.HttpResponseNotFound()
  else:
    game_number = request.GET['gamenumber']

  # get the game associated with this request
  try:
    game = Game.objects.get(number=game_number)
  except Game.DoesNotExist:
    print('couldn\'t find game with that number')
    return http.HttpResponseNotFound()

  if ('fetchlimit' in request.GET):
    # this is an initialization request; return fetchlimit most recent entries
    fetch_limit = request.GET['fetchlimit']
  else: 
    fetch_limit = 50

  # fetch relavent activities and respond
  activity = (Activity.objects
      .filter(game=game)
      .extra(order_by=['-datetime'])
      [:fetch_limit])
  activity_export = [{
        'activity': o.activity,
        'datetime': o.datetime.isoformat(),
        'player1_alias': o.player1.alias,
        'player2_alias': o.player2.alias,
      } for o in activity]
  json = simplejson.dumps(activity_export)
  return http.HttpResponse(json)


def scoreboard(request):
  players = Player.objects.extra(order_by = ['-kill_count'])
  json = simplejson.dumps([{'alias': o.alias,
                            'kill_count': o.kill_count,
                            'is_alive': o.is_alive} for o in players])
  return http.HttpResponse(json)


# decorator to bypass cookie requirement
@csrf_exempt
def handleSms(request):
  """View that handles incoming SMS commands."""
  # filter out non-post
  if(request.method != 'POST'):
    return http.HttpResponseNotAllowed('')

  print(request.body)
  s = Session(request.body)
  if(s.userType == 'HUMAN'):
    print 'HUMAN'
  elif(s.userType == 'NONE'):
    return _handleSendMessage(s)
  else:
    return http.HttpResponseNotAllowed('')

  user = s.fromaddress['id']
  game_number = s.to['id']
  # user = '12488253011'
  # game_number = '16178703381'

  # grab and validate message
  msg = s.initialText
  msg = msg.strip()
  if(re.match('[\r\n]', msg)):
    return _sendError('invalid characters.')
  user = user.strip()
  if((not user) or user == ''):
    return _sendError('invalid phone number.')
  elif(not re.match('^[0-9+]+$', user)):
    return _sendError('invalid characters in phone number.')

  # get the game associated with this message
  try:
    game = Game.objects.get(number = game_number)
  except Game.DoesNotExist:
    return _sendError('game does not exist!')

  # try to parse command
  msg_parsed = msg.split(None)
  if(len(msg_parsed) < 1 or len(msg_parsed) > 3):
    return _sendError('that\'s not a valid command.')

  ## dispatch command
  # commands we can answer without user
  msg_parsed[0] = msg_parsed[0].lower()
  if(msg_parsed[0] == "echo"):
    return _handleEcho(msg_parsed, user)
  elif(msg_parsed[0] == "join"):
    return _handleJoin(msg_parsed, user, game)

  # commands that need current user
  try:
    player = Player.objects.get(game = game, phone_number = user)
  except Player.DoesNotExist:
    return _sendError('you don\'t exist in this game; do you need to register?')

  # before we go on, check the player is alive
  if(not player.is_alive):
    return _sendError('It looks like you\'re already dead!')

  if (msg_parsed[0] == "kill"):
    return _handleKill(msg_parsed, player, game)
  # elif(msg_parsed[0] == "dead"):
  #   return _handleDead(msg_parsed, user)
  elif msg_parsed[0] == "secret":
    return _sendResponse(player.code)
  elif(msg_parsed[0] == "target"):
    return _handleTarget(msg_parsed, player, game)
  elif(msg_parsed[0] == "quit"):
    return _handleQuit(msg_parsed, player, game)

  # couldn't find that command
  return _sendError('that\'s not a valid command.')


def _handleEcho(msg_parsed, user):
  """expect msg: echo <repeated>"""
  if(len(msg_parsed) != 2):
    return _sendError('incorrect number of arguments.')
  return _sendResponse(str(user) + ' said: ' + msg_parsed[1])


def _handleJoin(msg_parsed, user, game):
  """expect msg: join <ldap> <alias>"""
  if(len(msg_parsed) != 3):
    return _sendError('incorrect number of arguments.')
  ldap = msg_parsed[1]
  alias = msg_parsed[2]

  if(game.registration_open is not True):
    return _sendError('registration for ' + game.name + ' is closed.')

  # Add a player to the game.
  try:
    code = random.randint(100, 999)
    code_str = str(code)
    player = game.player_set.create(
      phone_number = user,
      alias = alias,
      ldap = ldap,
      code = code_str)
    output = 'You are registered as alias ' + player.alias +\
        '. Your secret code is ' + code_str +'.'
    return _sendResponse(output)
  except IntegrityError:
    try:
      Player.objects.get(game = game, phone_number = user)
      _sendError('this phone is already registered for this game.')
    except Player.DoesNotExist:
      pass
    try:
      Player.objects.get(game = game, alias = alias)
      return _sendError('the alias ' + alias + ' is already taken.')
    except Player.DoesNotExist:
      pass
    try:
      Player.objects.get(game = game, ldap = ldap)
      return _sendError('the ldap ' + ldap + ' is already registered.')
    except Player.DoesNotExist:
      pass
    return _sendError('there was an error in the data you submitted =(')
  except DatabaseError as e:
    print e
    return _sendError('database error.')


def _handleKill(msg_parsed, player, game):
  """expect msg: kill <code>"""
  if(len(msg_parsed) != 2):
    return _sendError('incorrect number of arguments.'
        ' Did you forget to send your target\'s secret code?')

  if(not game.game_started):
    return _sendError('the game hasn\'t started yet!')

  target = player.target
  if target is None:
    return _sendError('you don\'t have a target. ' + ADMIN_MESSAGE)

  # since this function requires confirmation, set waiting_response
  target_code = msg_parsed[1]

  if target_code != target.code:
    return _wrongCode(player)
  else:
    return _killPlayer(player, target, game)


def _killPlayer(killer, target, game):
    target.is_alive = False
    target.save()

    killer.kill_count = killer.kill_count + 1
    killer.target = target.target
    killer.incorrect_codes = 0

    Activity.objects.create(game=game,
                            activity='killed',
                            player1=killer,
                            player2=target)

    _sendNewMessage("Looks like you're dead", target.phone_number, game.token)
    # winning state if the killer has been assigned him/herself
    if killer.target == killer:
      killer.target = None
      killer.save()
      # record in activity list
      Activity.objects.create(game=game,
                              activity='win',
                              player1=killer)
      return _sendResponse('Congrats. You win!')
    else:

      killer.save()
      if killer.target is None:
        return _sendError('Couldn\'t find new target. ' + ADMIN_MESSAGE)
      else:
        msg = 'Your new target is who/' + killer.target.ldap + '. Good luck.'
        return _sendResponse(msg)


def _wrongCode(player):
    player.incorrect_codes = player.incorrect_codes + 1
    if player.incorrect_codes > INCORRECT_CODE_LIMIT:
        return _forceQuitPlayer(
            'You have been lynched for brute-forcing the system... =(',
            player,
            game)
    else:
      player.save()
      return _sendError(
        'could not verify kill. you have %d/%d attempts left' %
        (INCORRECT_CODE_LIMIT-player.incorrect_codes, INCORRECT_CODE_LIMIT))


def _handleTarget(msg_parsed, player, game):
  """expect msg: target"""
  if(len(msg_parsed) != 1):
    return _sendError('incorrect number of arguments.')
  return _sendResponse('Your target is who/' + player.target.ldap)


def _handleQuit(msg_parsed, player, game):
  """expect msg: quit code"""
  if(len(msg_parsed) != 2):
    return _sendError('incorrect number of arguments.'
        ' Did you remember to send your secret code?')

  code = msg_parsed[1]
  if player.code != code:
    return _sendResponse('Wrong code. Who are you?')
  else:
    return _forceQuitPlayer('That\'s ok. Better luck next time.', player, game)


def _forceQuitPlayer(quit_msg, player, game):
  player.is_alive = False
  player.incorrect_codes = 0
  player.save()

  # record in activity list
  Activity.objects.create(game=game,
                          activity='quit',
                          player1=player)

  # get the hunter/target objects
  try:
    hunter = Player.objects.get(game = game,
                                is_alive = True,
                                target = player)
  except Player.DoesNotExist:
    return _sendError('Couldn\'t find your hunter.')
  if player.target is None:
    return _sendError('Couldn\'t find your target.')

  if(player.target == hunter):
    # there were only 2 players left; hunter wins
    hunter.target = None
    hunter.save()
    _sendNewMessage('Congrats. You win!', hunter.phone_number, game.token)

    # record in activity list
    Activity.objects.create(game=game,
                            activity='win',
                            player1=hunter)

  else:
    # change target of hunter and notify
    hunter.target = player.target
    hunter.save()
    _sendNewMessage('Your target quit. Your new target is who/' + target.ldap,
                    hunter.phone_number,
                    game.token)

  # accept defeat
  return _sendResponse(quit_msg)


def _handleSendMessage(s):
  """used to send messages other than replies"""
  if(s.parameters['outboundmsg'] is not None and
      s.parameters['outboundnum'] is not None):
    return _sendResponse(s.parameters['outboundmsg'],
                         s.parameters['outboundnum'])
  else:
    return http.HttpResponseBadRequest('')


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


def _sendResponse(text, to = None):
  t = Tropo()
  if(to is not None):
    t.call('+' + to, network = 'SMS')
  t.say([text])
  json = t.RenderJson()
  return http.HttpResponse(json)


def _sendError(explain):
  t = Tropo()
  t.say(['Error: ' + explain])
  json = t.RenderJson()
  return http.HttpResponse(json)
