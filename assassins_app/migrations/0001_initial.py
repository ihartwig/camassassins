# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Game'
        db.create_table('assassins_app_game', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40)),
            ('number', self.gf('django.db.models.fields.CharField')(unique=True, max_length=20)),
            ('token', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('registration_open', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('game_started', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('assassins_app', ['Game'])

        # Adding model 'Player'
        db.create_table('assassins_app_player', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('game', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assassins_app.Game'])),
            ('phone_number', self.gf('django.db.models.fields.CharField')(unique=True, max_length=20)),
            ('target_number', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('alias', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('ldap', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('is_alive', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('waiting_response', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
            ('kill_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('assassins_app', ['Player'])

        # Adding model 'Activity'
        db.create_table('assassins_app_activity', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('game', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assassins_app.Game'])),
            ('activity', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('assassins_app', ['Activity'])


    def backwards(self, orm):
        # Deleting model 'Game'
        db.delete_table('assassins_app_game')

        # Deleting model 'Player'
        db.delete_table('assassins_app_player')

        # Deleting model 'Activity'
        db.delete_table('assassins_app_activity')


    models = {
        'assassins_app.activity': {
            'Meta': {'object_name': 'Activity'},
            'activity': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'game': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['assassins_app.Game']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
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