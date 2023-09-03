# Generated by Django 4.2.4 on 2023-08-26 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Deliver',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('males', models.PositiveSmallIntegerField(default=0)),
                ('females', models.PositiveSmallIntegerField(default=0)),
                ('notes', models.TextField(blank=True, default='')),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=60)),
                ('message', models.TextField(blank=True, default='')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, default='')),
                ('project_file', models.FileField(upload_to='uploads/projects')),
                ('ceua_protocol', models.CharField(max_length=16)),
                ('ceua_file', models.FileField(upload_to='uploads/ceua')),
                ('slug', models.SlugField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Requisition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('protocol', models.CharField(editable=False, max_length=12, unique=True)),
                ('date', models.DateField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('males', models.PositiveSmallIntegerField(default=0)),
                ('females', models.PositiveSmallIntegerField(default=0)),
                ('author_notes', models.TextField(blank=True, default='')),
            ],
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('RE', 'Recebida'), ('PR', 'Em Produção'), ('CO', 'Concluída'), ('PA', 'Parcialmente concluída'), ('SU', 'Suspensa'), ('CA', 'Cancelada')], default='EN', max_length=2)),
                ('message', models.TextField(blank=True, default='')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=48, unique=True)),
                ('description', models.TextField(blank=True, default='')),
                ('slug', models.SlugField(blank=True, max_length=16, unique=True)),
                ('color', models.CharField(blank=True, choices=[('slate', 'slate'), ('gray', 'gray'), ('zinc', 'zinc'), ('neutral', 'neutral'), ('stone', 'stone'), ('red', 'red'), ('orange', 'orange'), ('amber', 'amber'), ('yellow', 'yellow'), ('lime', 'lime'), ('green', 'green'), ('emerald', 'emerald'), ('teal', 'teal'), ('cyan', 'cyan'), ('sky', 'sky'), ('blue', 'blue'), ('indigo', 'indigo'), ('violet', 'violet'), ('purple', 'purple'), ('fuchsia', 'fuchsia'), ('pink', 'pink'), ('rose', 'rose')], default='blue', max_length=7)),
            ],
        ),
    ]
