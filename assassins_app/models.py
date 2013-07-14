from django.db import models

class Game(models.Model):
  name = models.CharField(max_length=40, unique = True)
  number = models.CharField(max_length=20, unique = True)
  token = models.CharField(max_length = 200, unique = True)
  registration_open = models.BooleanField(default = False)
  game_started = models.BooleanField(default = False)

  def __unicode__(self):
    return self.name + ' (' + self.number + ')'


class Player(models.Model):
  game = models.ForeignKey(Game)
  # assume that we'll never have overlapping phone numbers
  phone_number = models.CharField(max_length = 20, unique = True)
  target_number = models.CharField(max_length = 20, null = True, blank = True)
  alias = models.CharField(max_length=200, unique = True)
  ldap = models.CharField(max_length=200, unique = True)
  is_alive = models.BooleanField(default = True)
  waiting_response = models.CharField(max_length=40, null = True, blank = True)
  kill_count = models.IntegerField(default=0)

  def __unicode__(self):
    return self.alias + ' (' + self.phone_number + ', ' + self.ldap + '@)'

class Activity(models.Model):
  game = models.ForeignKey(Game)
  activity = models.CharField(max_length = 500)
  datetime = models.DateTimeField(auto_now_add = True)
  player1 = models.ForeignKey(Player, related_name="+", null=True, blank=True)
  player2 = models.ForeignKey(Player, related_name="+", null=True, blank=True)
