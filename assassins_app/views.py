from assassins_app.models import Game, Player
from django.db import DatabaseError, IntegrityError
from django.http import HttpResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
import re
from tropo import Tropo, Session


# decorator to bypass cookie requirement
@csrf_exempt
def handleSms(request):
  """View that handles incoming SMS commands."""
  # filter out non-post
  if(request.method != 'POST'):
    return HttpResponseNotAllowed

  s = Session(request.body)
  user = s.fromaddress['id']
  game_number = s.to['id']
  # user = '12488253011'
  # game_number = '16178703381'

  # grab and validate message
  msg = request.POST['msg']
  msg = msg.strip()
  if(re.match('[\r\n]', msg)):
    return _sendError('invalid characters.')
  # user = request.POST['user']
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

  msg_parsed[0] = msg_parsed[0].lower()
  if(msg_parsed[0] == "echo"):
    return _handleEcho(msg_parsed, user)
  elif(msg_parsed[0] == "join"):
    return _handleJoin(msg_parsed, user, game)
  elif(msg_parsed[0] == "kill"):
    return _handleKill(msg_parsed, user)
  elif(msg_parsed[0] == "dead"):
    return _handleDead(msg_parsed, user)
  elif(msg_parsed[0] == "target"):
    return _handleTarget(msg_parsed, user)
  elif(msg_parsed[0] == "quit"):
    return _handleQuit(msg_parsed, user)
  elif(msg_parsed[0] == "yes" or msg_parsed[0] == "no"):
    return _handleAnswer(msg_parsed, user)

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
    player = game.player_set.create(
      phone_number = user,
      alias = alias,
      ldap = ldap)
    output = 'You are registered as alias ' + player.alias + ' with ldap ' +\
        player.ldap + ' for ' + game.name + '.'
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



def _handleKill(msg_parsed, user):
  """expect msg: kill"""
  if(len(msg_parsed) != 1):
    return _sendError('incorrect number of arguments.')


def _finishKill():
  pass


def _handleDeath(msg_parsed, user):
  """expect msg: dead"""
  if(len(msg_parsed) != 1):
    return _sendError('incorrect number of arguments.')


def _handleTarget(msg_parsed, user):
  """expect msg: target"""
  if(len(msg_parsed) != 1):
    return _sendError('incorrect number of arguments.')


def _handleQuit(msg_parsed, user):
  """expect msg: quit"""
  if(len(msg_parsed) != 1):
    return _sendError('incorrect number of arguments.')


def _finishQuit():
  pass


def _handleAnswer(msg_parsed, user):
  """expect msg: <yes | no>"""


def _sendResponse(text):
  t = Tropo()
  t.say([text])
  json = t.RenderJson()
  return HttpResponse(json)


def _sendError(explain):
  t = Tropo()
  t.say(['Error: ' + explain])
  json = t.RenderJson()
  return HttpResponse(json)
