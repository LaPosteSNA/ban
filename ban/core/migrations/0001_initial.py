# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators
import django.contrib.auth.models
import django.utils.timezone
from django.conf import settings
import ban.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(verbose_name='last login', null=True, blank=True)),
                ('is_superuser', models.BooleanField(verbose_name='superuser status', help_text='Designates that this user has all permissions without explicitly assigning them.', default=False)),
                ('username', models.CharField(help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=30, unique=True, validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.', 'invalid')], verbose_name='username', error_messages={'unique': 'A user with that username already exists.'})),
                ('first_name', models.CharField(verbose_name='first name', max_length=30, blank=True)),
                ('last_name', models.CharField(verbose_name='last name', max_length=30, blank=True)),
                ('email', models.EmailField(verbose_name='email address', max_length=254, blank=True)),
                ('is_staff', models.BooleanField(verbose_name='staff status', help_text='Designates whether the user can log into this admin site.', default=False)),
                ('is_active', models.BooleanField(verbose_name='active', help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', default=True)),
                ('date_joined', models.DateTimeField(verbose_name='date joined', default=django.utils.timezone.now)),
                ('company', models.CharField(verbose_name='Company', max_length=100, blank=True)),
                ('groups', models.ManyToManyField(help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', to='auth.Group', related_name='user_set', verbose_name='groups', related_query_name='user', blank=True)),
                ('user_permissions', models.ManyToManyField(help_text='Specific permissions for this user.', to='auth.Permission', related_name='user_set', verbose_name='user permissions', related_query_name='user', blank=True)),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='HouseNumber',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('version', models.SmallIntegerField(default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('number', models.CharField(max_length=16)),
                ('ordinal', models.CharField(max_length=16, blank=True)),
                ('cia', models.CharField(editable=False, max_length=100, blank=True)),
                ('created_by', models.ForeignKey(editable=False, null=True, related_name='housenumber_created', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Locality',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('version', models.SmallIntegerField(default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(verbose_name='name', max_length=200)),
                ('fantoir', models.CharField(max_length=9, null=True, blank=True)),
                ('created_by', models.ForeignKey(editable=False, null=True, related_name='locality_created', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(editable=False, null=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Municipality',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('version', models.SmallIntegerField(default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(verbose_name='name', max_length=200)),
                ('insee', models.CharField(max_length=5)),
                ('siren', models.CharField(max_length=9)),
                ('created_by', models.ForeignKey(editable=False, null=True, related_name='municipality_created', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(editable=False, null=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('name',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('version', models.SmallIntegerField(default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('center', ban.core.fields.HouseNumberField(verbose_name='center', geography=True, srid=4326)),
                ('source', models.CharField(max_length=64, blank=True)),
                ('comment', models.TextField(blank=True)),
                ('created_by', models.ForeignKey(editable=False, null=True, related_name='position_created', to=settings.AUTH_USER_MODEL)),
                ('housenumber', models.ForeignKey(to='core.HouseNumber')),
                ('modified_by', models.ForeignKey(editable=False, null=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Street',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('version', models.SmallIntegerField(default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(verbose_name='name', max_length=200)),
                ('fantoir', models.CharField(max_length=9, null=True, blank=True)),
                ('created_by', models.ForeignKey(editable=False, null=True, related_name='street_created', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(editable=False, null=True, to=settings.AUTH_USER_MODEL)),
                ('municipality', models.ForeignKey(to='core.Municipality')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='locality',
            name='municipality',
            field=models.ForeignKey(to='core.Municipality'),
        ),
        migrations.AddField(
            model_name='housenumber',
            name='locality',
            field=models.ForeignKey(to='core.Locality', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='housenumber',
            name='modified_by',
            field=models.ForeignKey(editable=False, null=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='housenumber',
            name='street',
            field=models.ForeignKey(to='core.Street', null=True, blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='position',
            unique_together=set([('housenumber', 'source')]),
        ),
        migrations.AlterUniqueTogether(
            name='housenumber',
            unique_together=set([('number', 'ordinal', 'street', 'locality')]),
        ),
    ]
