from django.db import models

class Game(models.Model):
  name = models.CharField(max_length=40, unique = True)
  registration_open = models.BooleanField(default = False)
  game_started = models.BooleanField(default = False)

  def __unicode__(self):
    return self.name


class Player(models.Model):
  game = models.ForeignKey(Game)
  # assume that we'll never have overlapping phone numbers
  phone_number = models.CharField(max_length = 20, unique = True)
  target_number = models.CharField(max_length = 20, null = True)
  alias = models.CharField(max_length=200, unique = True)
  ldap = models.CharField(max_length=200, unique = True)
  is_alive = models.BooleanField(default = True)
  waiting_response = models.CharField(max_length=40, null = True)

  def __unicode__(self):
    return self.alias + '(' + self.phone_number + ', ' + self.ldap + '@)'
