print('我是stark')
from django.shortcuts import HttpResponse,render,redirect
from django.utils.safestring import mark_safe
from django.conf.urls import url
from stark.service import v1
from crm import models
from django.forms import ModelForm
class SchoolConfig(v1.StarkConfig):
    list_display = ['id','title']
v1.site.register(models.School,SchoolConfig)

class CourseConfig(v1.StarkConfig):
    list_display = ['id','name']
v1.site.register(models.Course,CourseConfig)


class DepartmentConfig(v1.StarkConfig):
    list_display = ['id','title','code']
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
        return obj.depart.title#对象.字段

    list_display = ['id','name','email',display_gender,display_depart]

    #条件筛选
    comb_filter = [
        #  FilterOption('字段', 是否多选, 条件, 是否是choice),
        v1.FilterOption('depart'),#, condition={'id__gt': 3}
    ]

v1.site.register(models.UserInfo,UserInfoConfig)