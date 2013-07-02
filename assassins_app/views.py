# from assassins_app import 
from django.http import HttpResponse, HttpResponseNotAllowed
# decorator to bypass cookie requirement
from django.views.decorators.csrf import csrf_exempt
import re
from tropo import Tropo, Session


@csrf_exempt
def handleSms(request):
  """View that handles incoming SMS commands."""
  # filter out non-post
  if(request.method != 'POST'):
    return HttpResponseNotAllowed

  msg = request.POST['msg']
  msg = msg.strip()
  user = request.POST['user']
  # check for valid message
  if re.match('[\r\n]', msg):
    return _sendError('invalid characters.')

  # try to parse command
  msg_parsed = msg.split(None)
  if(len(msg_parsed) < 1 or len(msg_parsed) > 4):
    return _sendError('that\'s not a valid command.')

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
  return _sendResponse(str(user) + 'said: ' + msg_parsed[1])


def _handleJoin(msg_parsed, user):
  """expect msg: join <game_name> <ldap> <alias>"""
  if(len(msg_parsed) != 4):
    return _sendError('incorrect number of arguments.')


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
