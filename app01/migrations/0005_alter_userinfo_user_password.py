# Generated by Django 4.2.7 on 2023-11-11 02:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0004_alter_userinfo_user_depart'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='user_password',
            field=models.CharField(max_length=16, verbose_name='密码'),
        ),
    ]
