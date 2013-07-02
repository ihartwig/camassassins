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

  # grab and validate message
  msg = request.POST['msg']
  msg = msg.strip()
  if(re.match('[\r\n]', msg)):
    return _sendError('invalid characters.')
  user = request.POST['user']
  user = user.strip()
  if((not user) or user == ''):
    return _sendError('invalid phone number.')
  elif(not re.match('^[0-9+]+$', user)):
    return _sendError('invalid characters in phone number.')
  

  # try to parse command
  msg_parsed = msg.split(None)
  if(len(msg_parsed) < 1 or len(msg_parsed) > 4):
    return _sendError('that\'s not a valid command.')

  msg_parsed[0] = msg_parsed[0].lower()
  if(msg_parsed[0] == "echo"):
    return _handleEcho(msg_parsed, user)
  elif(msg_parsed[0] == "join"):
    return _handleJoin(msg_parsed, user)
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


def _handleJoin(msg_parsed, user):
  """expect msg: join <game_name> <ldap> <alias>"""
  if(len(msg_parsed) != 4):
    return _sendError('incorrect number of arguments.')
  game_name = msg_parsed[1]
  ldap = msg_parsed[2]
  alias = msg_parsed[3]

  # Retrieve game object.
  try:
    game = Game.objects.get(name = game_name)
  except DoesNotExist:
    return _sendError('game ' + game_name + ' does not exist!')

  # Add a player to the game.
  try:
    player = game.player_set.create(
      phone_number = user,
      alias = alias,
      ldap = ldap)
    output = 'You are registered as alias ' + player.alias + ' with ldap ' +\
        player.ldap + '.'
    return _sendResponse(output)
  except IntegrityError:
    try:
      Player.objects.get(phone_number = user)
      _sendError('this phone is already registered for this game.')
    except Player.DoesNotExist:
      pass
    try:
      Player.objects.get(alias = alias)
      return _sendError('the alias ' + alias + ' is already taken.')
    except Player.DoesNotExist:
      pass
    try:
      Player.objects.get(ldap = ldap)
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
