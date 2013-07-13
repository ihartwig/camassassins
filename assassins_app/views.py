from assassins_app.models import Game, Player
from django import http
from django.db import DatabaseError, IntegrityError
from django.views.decorators.csrf import csrf_exempt
import re
import requests
from tropo import Tropo, Session, Say


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
  msg = request.POST['msg']
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
  if(player.waiting_response):
    # we're waiting for a response, dispatch to answer
    return _handleAnswer(msg_parsed, player, game)
  elif(msg_parsed[0] == "kill"):
    return _handleKill(msg_parsed, user, game)
  # elif(msg_parsed[0] == "dead"):
  #   return _handleDead(msg_parsed, user)
  elif(msg_parsed[0] == "target"):
    return _handleTarget(msg_parsed, player, game)
  elif(msg_parsed[0] == "quit"):
    return _handleQuit(msg_parsed, player, game)

  # couldn't find that command
  return _sendError('that\'s not a valid command.')


def displayScoreboard(request):
  pass


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



def _handleKill(msg_parsed, user, game):
  """expect msg: kill"""
  if(len(msg_parsed) != 1):
    return _sendError('incorrect number of arguments.')
  
  if(not game.game_started):
    return _sendError('the game hasn\'t started yet!')

  # get player and target db objects
  try:
    player = Player.objects.get(game = game, phone_number = user)
  except Player.DoesNotExist:
    return _sendError('you don\'t exist in this game; do you need to register?')
  try:
    target = Player.objects.get(game = game,
                                phone_number = player.target_number)
  except Player.DoesNotExist:
    return _sendError('you don\'t have a target. Please notify the game admin.')

  # since this function requires confirmation, set waiting_response
  player.waiting_response = 'killer'
  player.save()
  target.waiting_response = 'killed'
  target.save()

  msg = player.alias + ' reports killing you. Please confirm [yes/no].'
  if(not _sendNewMessage(msg, player.target_number, game.token)):
    # sending message failed; retreat.
    player.waiting_response = ''
    player.save()
    target.waiting_response = ''
    target.save()
    return _sendError('could not verify kill.')

  return _sendResponse('Verifying kill...')


def _finishKill(answer, player, game):
  try:
    killer = Player.objects.get(game=game,
                                is_alive=True,
                                target_number=player.phone_number)
  except Player.DoesNotExist:
    return _sendError('couldn\'t find your killer in the game.')
  
  if(answer == 'yes'):
    # player is dead
    player.is_alive = False
    player.save()
    killer.kill_count = killer.kill_count + 1
    killer.waiting_response = ''
    killer.save()
    if(player.target_number == killer.phone_number):
      # there were only 2 players left; killer wins
      killer.target_number = ''
      killer.save()
      _sendNewMessage('Congrats. You win!', killer.phone_number, game.token)
      return _sendResponse('Death recorded.')
    else:
      # transfer target and notify kill
      killer.target_number = player.target_number
      try:
        target = Player.objects.get(game = game,
                                    phone_number = killer.target_number)
        msg = 'Your new target is teams/' + target.ldap + '. Good luck.'
        _sendNewMessage(msg, killer.phone_number, game.token)
      except Player.DoesNotExist:
        _sendNewMessage('Couldn\'t find new target. Please contact game admin',
                        killer.phone_number,
                        game.token)
      killer.save()
      return _sendResponse('Death recorded.')
  else:
    # answered no. reset state.
    player.waiting_response = ''
    player.save()
    killer.waiting_response = ''
    killer.save()
    _sendNewMessage('Target rejected kill.', killer.phone_number, game.token)
    return _sendResponse('Ok. Wish your assassin luck next time.')



# def _handleDeath(msg_parsed, user):
#   """expect msg: dead"""
#   if(len(msg_parsed) != 1):
#     return _sendError('incorrect number of arguments.')


def _handleTarget(msg_parsed, player, game):
  """expect msg: target"""
  if(len(msg_parsed) != 1):
    return _sendError('incorrect number of arguments.')
  try:
    target = Player.objects.get(game = game,
                                phone_number = player.target_number)
  except Player.DoesNotExist:
    return _sendError('Couldn\'t find your target.')
  return _sendResponse('Your target is ' + target.ldap + '@google.com.')


def _handleQuit(msg_parsed, player, game):
  """expect msg: quit"""
  if(len(msg_parsed) != 1):
    return _sendError('incorrect number of arguments.')

  player.waiting_response = 'quitting'
  player.save()

  return _sendResponse('Are you sure you want to quit? ' +
                           'Please respond with [yes/no].')


def _finishQuit(answer, player, game):
  if(answer == 'no'):
    player.waiting_response = ''
    player.save()
    return _sendResponse('It\'s ok. We forgive you.')
  else:
    # kill the current player
    player.is_alive = False
    player.save()

    # get the hunter/target objects
    try:
      hunter = Player.objects.get(game = game,
                                  is_alive = True,
                                  target_number = player.phone_number)
    except Player.DoesNotExist:
      return _sendError('Couldn\'t find your hunter.')
    try:
      target = Player.objects.get(game = game,
                                  phone_number = player.target_number)
    except Player.DoesNotExist:
      return _sendError('Couldn\'t find your target.')

    if(player.target_number == hunter.phone_number):
      # there were only 2 players left; hunter wins
      hunter.target_number = ''
      hunter.save()
      _sendNewMessage('Congrats. You win!', hunter.phone_number, game.token)

    else:
      # change target of hunter and notify
      hunter.target_number = player.target_number
      hunter.save()
      _sendNewMessage('Your target quit. Your new target is ' + target.ldap +
                          '@google.com.',
                      hunter.phone_number,
                      game.token)

    # accept defeat
    return _sendResponse('That\'s ok. Better luck next time.')


def _handleAnswer(msg_parsed, player, game):
  """expect msg: <yes | no>"""
  answer = msg_parsed[0].lower()
  if(not (answer == 'yes' or answer == 'no')):
    return _sendError('please respond with [yes/no].')
  # dispatch based on the waiting state
  waiting_response = player.waiting_response
  if(waiting_response == 'killer'):
    return _sendResponse('We\'re still waiting on your victim.')
  elif(waiting_response == 'killed'):
    return _finishKill(answer, player, game)
  elif(waiting_response == 'quitting'):
    return _finishQuit(answer, player, game)
  else:
    return _sendError('You\'re waiting for something, but I can\'t tell what')


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
