from django.db import models

# Create your models here.

class Player(models.Model):
  # assume that we'll never have overlapping phone numbers
  phone_number = models.CharField(max_length=20)
  target_number = models.CharField(max_length=20)
  alias = models.CharField(max_length=200)
  ldap = models.CharField(max_length=200)
  is_alive = models.SmallIntegerField()
  waiting_response = models.CharField(max_length=40)

  def __unicode__(self):
    return self.phone_number
