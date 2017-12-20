print('我是stark')
from django.shortcuts import HttpResponse,render,redirect
from django.utils.safestring import mark_safe
from django.conf.urls import url
from stark.service import v1
from app04 import models
from django.forms import ModelForm

class RoleConfig(v1.StarkConfig):
    list_display = ['id','title']
v1.site.register(models.Role,RoleConfig)


class DepartmentConfig(v1.StarkConfig):
    list_display = ['id','caption']
v1.site.register(models.Department,DepartmentConfig)


class UserInfoConfig(v1.StarkConfig):
    show_search_form = True  # 搜索框
    search_fields = ['name__contains', 'email__contains']  # 模糊搜索

    show_actions = True  # 批量操作框
    # 批量删除
    def multi_del(self, request):
        pk_list = request.POST.getlist('pk')  # 得到所有的勾选的项
        self.model_class.objects.filter(id__in=pk_list).delete()
        return HttpResponse('删除成功')
        # return redirect("http://www.baidu.com")

    multi_del.desc_text = "批量删除"  # 给函数内部加一个字段
    actions = [multi_del]  # 给actions加入定制的功能

    def display_gender(self,obj=None,is_header=False):
        if is_header:
            return '性别'
        return obj.get_gender_display()#get_字段名，可拿出choices里的内容
    def display_depart(self,obj=None,is_header=False):
        if is_header:
            return '部门'
        return obj.depart.caption#对象.字段
    def display_roles(self,obj=None,is_header=False):
        if is_header:
            return '角色'
        html = []
        role_list = obj.roles.all()
        for role in role_list:
            html.append(role.title)
        return "、".join(html)#多对多，循环取出，用顿号隔开显示
    list_display = ['id','name','email',display_gender,display_depart,display_roles]

    #条件筛选
    comb_filter = [
        #  FilterOption('字段', 是否多选, 条件, 是否是choice),
        v1.FilterOption('gender', is_choice=True),#关键字传参，代表是choice
        v1.FilterOption('depart'),#, condition={'id__gt': 3}
        v1.FilterOption('roles', True),#True传入，代表是多选
    ]

v1.site.register(models.UserInfo,UserInfoConfig)