# Generated by Django 2.2.10 on 2020-02-15 20:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('booker_app', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='book',
            old_name='cover_image',
            new_name='cover_image_adress',
        ),
    ]
