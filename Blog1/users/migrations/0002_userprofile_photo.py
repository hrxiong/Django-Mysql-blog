# Generated by Django 2.0.5 on 2018-05-12 06:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='photo',
            field=models.ImageField(default='photos/user1.jpg', upload_to='upload'),
        ),
    ]
