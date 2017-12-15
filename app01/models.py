from django.db import models

# Create your models here.
class UserInfo(models.Model):
    name=models.CharField(max_length=32)
    pwd=models.CharField(max_length=32)
    email=models.EmailField(max_length=32)
    tp=models.ForeignKey('Type')

    class Meta:
        verbose_name_plural = "用户表"
    def __str__(self):
        return self.name
class Type(models.Model):
    name=models.CharField(max_length=32)
    role=models.ManyToManyField('Role')

    class Meta:
        verbose_name_plural = "类型表"

    def __str__(self):
        return self.name

class Role(models.Model):
    name=models.CharField(max_length=32)
    salary=models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "角色表"
    def __str__(self):
        return self.name



class Host(models.Model):
    hostname = models.CharField(verbose_name='主机名',max_length=32)
    ip = models.GenericIPAddressField(verbose_name="IP",protocol='ipv4')
    port = models.IntegerField(verbose_name='端口')