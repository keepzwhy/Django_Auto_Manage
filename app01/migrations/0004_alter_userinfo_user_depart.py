# Generated by Django 4.2.7 on 2023-11-11 02:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0003_alter_userinfo_user_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='user_depart',
            field=models.SmallIntegerField(choices=[(1, '开发部门'), (2, '测试部门'), (3, '运维部门')], verbose_name='部门'),
        ),
    ]