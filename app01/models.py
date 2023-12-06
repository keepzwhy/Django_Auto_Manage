from django.db import models

# Create your models here.
class UserInfo(models.Model):
    user_name = models.CharField(max_length=16,verbose_name='用户名')
    user_password = models.CharField(max_length=16,verbose_name='密码')
    user_age = models.IntegerField(verbose_name='年龄')
    gender_choice = (
        (1,'男'),
        (2,'女'),
    )
    user_gender = models.SmallIntegerField(choices=gender_choice,verbose_name='性别')
    depart_choice = (
        (1,'开发部门'),
        (2,'测试部门'),
        (3,'运维部门')
    )
    user_depart = models.SmallIntegerField(choices=depart_choice,verbose_name='部门')
    user_time = models.DateField(max_length=24,verbose_name='入职时间')