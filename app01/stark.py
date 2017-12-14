print('我是stark')
from stark.service import v1
from app01 import models
from django.utils.safestring import mark_safe
class UserinfoConfig(v1.StarkConfig):
    '''
    自己定义的派生类，可以有29种额外的显示方式，效果与admin相同
    '''
    def checkbox(self,obj=None,is_header=False):
        if is_header:
            return '选择'
        return mark_safe('<input type="checkbox" name="pk" value="%s" >' %(obj.id,))

    list_display=[checkbox,'id','name']


#相应的注册
#第二个参数传入自己写的类时，可以拥有自己写的类中的额外的方法
v1.site.register(models.UserInfo,UserinfoConfig)
v1.site.register(models.Role)
v1.site.register(models.Type)