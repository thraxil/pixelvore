# flake8: noqa
# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Image'
        db.create_table('main_image', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('url', self.gf('django.db.models.fields.URLField')(default='', max_length=200)),
            ('ahash', self.gf('django.db.models.fields.CharField')(default='', max_length=256, null=True)),
            ('ext', self.gf('django.db.models.fields.CharField')(default='.jpg', max_length=256)),
        ))
        db.send_create_signal('main', ['Image'])

        # Adding model 'Tag'
        db.create_table('main_tag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('tag', self.gf('django.db.models.fields.CharField')(default='', max_length=256)),
        ))
        db.send_create_signal('main', ['Tag'])

        # Adding model 'ImageTag'
        db.create_table('main_imagetag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Image'])),
            ('tag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Tag'])),
        ))
        db.send_create_signal('main', ['ImageTag'])


    def backwards(self, orm):
        # Deleting model 'Image'
        db.delete_table('main_image')

        # Deleting model 'Tag'
        db.delete_table('main_tag')

        # Deleting model 'ImageTag'
        db.delete_table('main_imagetag')


    models = {
        'main.image': {
            'Meta': {'object_name': 'Image'},
            'ahash': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256', 'null': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'ext': ('django.db.models.fields.CharField', [], {'default': "'.jpg'", 'max_length': '256'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200'})
        },
        'main.imagetag': {
            'Meta': {'object_name': 'ImageTag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Image']"}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Tag']"})
        },
        'main.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'tag': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256'})
        }
    }

    complete_apps = ['main']
