# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Activity.player1'
        db.add_column('assassins_app_activity', 'player1',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['assassins_app.Player']),
                      keep_default=False)

        # Adding field 'Activity.player2'
        db.add_column('assassins_app_activity', 'player2',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['assassins_app.Player']),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Activity.player1'
        db.delete_column('assassins_app_activity', 'player1_id')

        # Deleting field 'Activity.player2'
        db.delete_column('assassins_app_activity', 'player2_id')


    models = {
        'assassins_app.activity': {
            'Meta': {'object_name': 'Activity'},
            'activity': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'game': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['assassins_app.Game']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'player1': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['assassins_app.Player']"}),
            'player2': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['assassins_app.Player']"})
        },
        'assassins_app.game': {
            'Meta': {'object_name': 'Game'},
            'game_started': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'number': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'}),
            'registration_open': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'token': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'})
        },
        'assassins_app.player': {
            'Meta': {'object_name': 'Player'},
            'alias': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'game': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['assassins_app.Game']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_alive': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'kill_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'ldap': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'}),
            'target_number': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'waiting_response': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['assassins_app']