# Generated by Django 4.2.4 on 2023-09-04 23:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customuser',
            options={'ordering': ['id'], 'verbose_name': 'Пользователь', 'verbose_name_plural': 'Пользователи'},
        ),
        migrations.RemoveConstraint(
            model_name='customuser',
            name='usrname_email_constraint',
        ),
    ]
